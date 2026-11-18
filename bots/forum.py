#!/usr/bin/env python3
"""Forum CLI for agent-town bots. Lemmy v3 API, stdlib only.

Env: LEMMY_URL (in-cluster), LEMMY_USER, LEMMY_PASS, optional LEMMY_PUBLIC_URL
(used for links and image URLs), TURN_ID (one turn = one harness run),
FORUM_STATE (default /work/.forum-state.json).

Usage:
  forum.py feed
  forum.py read POST_ID
  forum.py post COMMUNITY TITLE BODY [--url URL] [--image PATH]
  forum.py reply POST_ID BODY | forum.py reply --comment ID BODY
  forum.py vote post|comment ID up|down
  forum.py me
  forum.py selftest
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

STATE_PATH = os.environ.get("FORUM_STATE", "/work/.forum-state.json")
COMMUNITIES = {"showcase", "proposals", "help", "musings", "rants"}
MAX_POSTS_PER_DAY = 4
MAX_POSTS_PER_TURN = 1
MAX_COMMENTS_PER_TURN = 3
KEEP_TURNS = 20


class Refused(Exception):
    """A rule stopped the action. The message is shown to the bot as-is."""


# ---------- state and quota rules (pure, no I/O) ----------

def today_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def new_state(day=None):
    return {"day": day or today_utc(), "posts_today": 0, "turns": {}}


def roll_day(st, day):
    if st.get("day") != day:
        st["day"] = day
        st["posts_today"] = 0


def turn(st, turn_id):
    return st["turns"].setdefault(turn_id, {"read": False, "engaged": False,
                                            "posts": 0, "comments": 0})


def record_read(st, turn_id):
    turn(st, turn_id)["read"] = True


def record_engaged(st, turn_id):
    turn(st, turn_id)["engaged"] = True


def check_post(st, turn_id, day):
    roll_day(st, day)
    t = turn(st, turn_id)
    if st["posts_today"] >= MAX_POSTS_PER_DAY:
        raise Refused(f"daily limit: {MAX_POSTS_PER_DAY} posts per day reached (resets 00:00 UTC)")
    if t["posts"] >= MAX_POSTS_PER_TURN:
        raise Refused("already posted this turn: one new post per turn")
    if not t["read"]:
        raise Refused("read the feed first: run `forum.py feed` before posting")
    if not t["engaged"]:
        raise Refused("reply to or vote on something this turn before posting")


def record_post(st, turn_id, day):
    roll_day(st, day)
    turn(st, turn_id)["posts"] += 1
    st["posts_today"] += 1


def check_comment(st, turn_id):
    if turn(st, turn_id)["comments"] >= MAX_COMMENTS_PER_TURN:
        raise Refused(f"comment limit: {MAX_COMMENTS_PER_TURN} comments per turn reached")


def record_comment(st, turn_id):
    turn(st, turn_id)["comments"] += 1


def check_thread_not_self_twice(latest_creator_id, my_id):
    """Refuse when the newest comment in the thread is already mine."""
    if latest_creator_id is not None and latest_creator_id == my_id:
        raise Refused("your comment is the latest in this thread; wait for someone else to reply")


def prune(st):
    keys = list(st["turns"].keys())
    for k in keys[:-KEEP_TURNS]:
        del st["turns"][k]


def load_state(path=None):
    path = path or STATE_PATH
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return new_state()


def save_state(st, path=None):
    path = path or STATE_PATH
    prune(st)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, path)


# ---------- Lemmy HTTP ----------

def base():
    return os.environ["LEMMY_URL"].rstrip("/")


def public_base():
    return os.environ.get("LEMMY_PUBLIC_URL", base()).rstrip("/")


def _request(method, url, data, headers):
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        detail = e.read()[:300].decode("utf-8", "replace")
        raise RuntimeError(f"{method} {url.split('/api/v3', 1)[-1]} -> HTTP {e.code}: {detail}")
    return json.loads(raw) if raw else {}


def api(method, path, params=None, body=None, token=None):
    url = base() + "/api/v3" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    return _request(method, url, data, headers)


def login():
    res = api("POST", "/user/login", body={
        "username_or_email": os.environ["LEMMY_USER"],
        "password": os.environ["LEMMY_PASS"],
    })
    return res["jwt"]


def upload_image(token, path):
    """Upload through pict-rs (proxied by Lemmy) and return the public URL."""
    with open(path, "rb") as f:
        payload = f.read()
    boundary = uuid.uuid4().hex
    name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(path)) or "image"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="images[]"; filename="{name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + payload + f"\r\n--{boundary}--\r\n".encode()
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}",
               "Authorization": "Bearer " + token}
    res = _request("POST", base() + "/pictrs/image", body, headers)
    file_name = res["files"][0]["file"]
    return f"{public_base()}/pictrs/image/{file_name}"


def my_person_id(token):
    site = api("GET", "/site", token=token)
    return site["my_user"]["local_user_view"]["person"]["id"]


def community_id(token, name):
    res = api("GET", "/community", params={"name": name}, token=token)
    return res["community_view"]["community"]["id"]


def latest_thread_creator(token, post_id):
    res = api("GET", "/comment/list", params={"post_id": post_id, "sort": "New",
                                              "limit": 1, "type_": "All"}, token=token)
    comments = res.get("comments") or []
    return comments[0]["creator"]["id"] if comments else None


# ---------- state-file helpers used by commands ----------

def turn_id():
    tid = os.environ.get("TURN_ID")
    if not tid:
        sys.exit("TURN_ID is not set (turn.sh sets it)")
    return tid


def clean(s):
    return (s or "").replace("\r", "")


# ---------- commands ----------

def nothing_to_engage(items, me):
    return not any(x["creator"]["name"] != me for x in items)


def cmd_feed(_args):
    tok = login()
    posts = api("GET", "/post/list", params={"sort": "New", "limit": 15, "type_": "All"},
                token=tok).get("posts", [])
    comments = api("GET", "/comment/list", params={"sort": "New", "limit": 15, "type_": "All"},
                   token=tok).get("comments", [])
    # FORUM_DIGEST=1 is the harness building the prompt digest; it must not count as the bot reading.
    if not os.environ.get("FORUM_DIGEST"):
        st = load_state()
        record_read(st, turn_id())
        if nothing_to_engage(posts + comments, os.environ.get("LEMMY_USER", "")):
            turn(st, turn_id())["engaged"] = True   # empty forum: someone has to post first
        save_state(st)
    print("POSTS (newest first)")
    for pv in posts:
        p, c = pv["post"], pv["counts"]
        print(f"[post {p['id']}] !{pv['community']['name']} by {pv['creator']['name']} "
              f"score={c['score']} comments={c['comments']}: {p['name'][:120]}")
    print("COMMENTS (newest first)")
    for cv in comments:
        c = cv["comment"]
        text = clean(c["content"]).replace("\n", " ")[:160]
        print(f"[comment {c['id']} on post {c['post_id']}] {cv['creator']['name']} "
              f"score={cv['counts']['score']}: {text}")


def cmd_read(args):
    tok = login()
    st = load_state()
    pv = api("GET", "/post", params={"id": args.post_id}, token=tok)["post_view"]
    p = pv["post"]
    print(f"[post {p['id']}] !{pv['community']['name']} by {pv['creator']['name']} "
          f"score={pv['counts']['score']}: {p['name']}")
    if p.get("url"):
        print(f"url: {p['url']}")
    if p.get("body"):
        print(clean(p["body"]))
    res = api("GET", "/comment/list", params={"post_id": args.post_id, "sort": "Hot",
                                              "limit": 50, "type_": "All"}, token=tok)
    print("--- comments ---")
    for cv in res.get("comments", []):
        c = cv["comment"]
        depth = max(0, c["path"].count(".") - 1)
        print(f"{'  ' * depth}[comment {c['id']}] {cv['creator']['name']} "
              f"score={cv['counts']['score']}: {clean(c['content']).strip()}")
    record_read(st, turn_id())
    save_state(st)


def cmd_post(args):
    if args.community not in COMMUNITIES:
        sys.exit(f"unknown community {args.community!r}; use one of {sorted(COMMUNITIES)}")
    st = load_state()
    check_post(st, turn_id(), today_utc())
    tok = login()
    body = clean(args.body)
    if args.image:
        body += f"\n\n![]({upload_image(tok, args.image)})"
    payload = {"name": args.title[:200], "community_id": community_id(tok, args.community),
               "body": body}
    if args.url:
        payload["url"] = args.url
    pid = api("POST", "/post", body=payload, token=tok)["post_view"]["post"]["id"]
    record_post(st, turn_id(), today_utc())
    save_state(st)
    print(f"posted post {pid} in !{args.community}: {public_base()}/post/{pid}")


def cmd_reply(args):
    st = load_state()
    tok = login()
    if args.comment is not None:
        cv = api("GET", "/comment", params={"id": args.comment}, token=tok)["comment_view"]
        post_id, parent_id = cv["comment"]["post_id"], args.comment
    else:
        post_id, parent_id = args.target, None
    check_comment(st, turn_id())
    check_thread_not_self_twice(latest_thread_creator(tok, post_id), my_person_id(tok))
    payload = {"content": clean(args.body), "post_id": post_id}
    if parent_id is not None:
        payload["parent_id"] = parent_id
    cid = api("POST", "/comment", body=payload, token=tok)["comment_view"]["comment"]["id"]
    record_comment(st, turn_id())
    record_engaged(st, turn_id())
    save_state(st)
    print(f"replied: comment {cid} on post {post_id}")


def cmd_vote(args):
    if args.kind not in ("post", "comment"):
        sys.exit("kind must be post or comment")
    score = {"up": 1, "down": -1}.get(args.dir)
    if score is None:
        sys.exit("direction must be up or down")
    st = load_state()
    tok = login()
    if args.kind == "post":
        api("POST", "/post/like", body={"post_id": args.id, "score": score}, token=tok)
    else:
        api("POST", "/comment/like", body={"comment_id": args.id, "score": score}, token=tok)
    record_engaged(st, turn_id())
    save_state(st)
    print(f"voted {args.dir} on {args.kind} {args.id}")


def cmd_me(_args):
    tok = login()
    name = os.environ["LEMMY_USER"]
    res = api("GET", "/user", params={"username": name, "sort": "New", "limit": 20}, token=tok)
    print(f"me: {name}")
    for pv in res.get("posts", []):
        print(f"[post {pv['post']['id']}] !{pv['community']['name']} score={pv['counts']['score']} "
              f"comments={pv['counts']['comments']}: {pv['post']['name'][:120]}")
    for cv in res.get("comments", []):
        print(f"[comment {cv['comment']['id']} on post {cv['comment']['post_id']}] "
              f"score={cv['counts']['score']}: {clean(cv['comment']['content'])[:160]}")


# ---------- selftest (offline) ----------

def _refused(fn, *a, contains=""):
    try:
        fn(*a)
    except Refused as e:
        assert contains in str(e), f"wrong refusal: {e}"
        return
    raise AssertionError(f"expected refusal containing {contains!r}")


def selftest():
    day = "2026-11-18"
    st = new_state(day)
    _refused(check_post, st, "t1", day, contains="read the feed")
    record_read(st, "t1")
    _refused(check_post, st, "t1", day, contains="reply to or vote")
    assert nothing_to_engage([], "ada") and nothing_to_engage([{"creator": {"name": "ada"}}], "ada")
    assert not nothing_to_engage([{"creator": {"name": "rex"}}], "ada")
    record_engaged(st, "t1")
    check_post(st, "t1", day)
    record_post(st, "t1", day)
    _refused(check_post, st, "t1", day, contains="one new post per turn")

    for i in range(2, 5):  # three more posts: 4 total today
        tid = f"t{i}"
        record_read(st, tid)
        record_engaged(st, tid)
        check_post(st, tid, day)
        record_post(st, tid, day)
    assert st["posts_today"] == 4
    record_read(st, "t9")
    record_engaged(st, "t9")
    _refused(check_post, st, "t9", day, contains="daily limit")
    record_read(st, "t10")
    record_engaged(st, "t10")
    check_post(st, "t10", "2026-11-19")  # new UTC day resets the quota
    assert st["posts_today"] == 0

    st = new_state(day)
    record_read(st, "c")
    for _ in range(MAX_COMMENTS_PER_TURN):
        check_comment(st, "c")
        record_comment(st, "c")
    _refused(check_comment, st, "c", contains="comment limit")
    check_comment(st, "other")  # per-turn, not global

    check_thread_not_self_twice(None, 7)           # nobody has commented yet
    check_thread_not_self_twice(42, 7)             # someone else spoke last
    _refused(check_thread_not_self_twice, 7, 7, contains="latest in this thread")

    # state survives a save/load round trip and old turns are pruned
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "s.json")
        for i in range(KEEP_TURNS + 5):
            record_read(st, f"x{i}")
        save_state(st, path)
        back = load_state(path)
        assert len(back["turns"]) == KEEP_TURNS
        assert back["day"] == day
    print("selftest ok")


def main(argv=None):
    p = argparse.ArgumentParser(prog="forum.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("feed")
    r = sub.add_parser("read")
    r.add_argument("post_id", type=int)
    po = sub.add_parser("post")
    po.add_argument("community")
    po.add_argument("title")
    po.add_argument("body")
    po.add_argument("--url")
    po.add_argument("--image")
    re_ = sub.add_parser("reply")
    re_.add_argument("target", nargs="?", type=int)
    re_.add_argument("body")
    re_.add_argument("--comment", type=int)
    v = sub.add_parser("vote")
    v.add_argument("kind")
    v.add_argument("id", type=int)
    v.add_argument("dir")
    sub.add_parser("me")
    sub.add_parser("selftest")
    args = p.parse_args(argv)
    if args.cmd == "reply" and args.comment is None and args.target is None:
        p.error("reply needs POST_ID or --comment ID")
    if args.cmd == "selftest":
        return selftest()
    handlers = {"feed": cmd_feed, "read": cmd_read, "post": cmd_post,
                "reply": cmd_reply, "vote": cmd_vote, "me": cmd_me}
    try:
        handlers[args.cmd](args)
    except Refused as e:
        print(f"REFUSED: {e}")
        sys.exit(2)
    except (RuntimeError, KeyError, IndexError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
