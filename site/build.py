#!/usr/bin/env python3
"""Build the Pages site: town/ and reports/ markdown -> styled HTML in _site/. Other files copied as-is.
Needs `pip install markdown`. Usage: python3 site/build.py [OUT]"""
import html, os, re, shutil, sys
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_site"))
_style = open(os.path.join(ROOT, "site", "style.css")).read()
_cut = _style.index("@import")  # the Hallmark stamp stays the first line of the inlined CSS
CSS = _style[:_cut] + "".join(open(os.path.join(ROOT, "site", f)).read() for f in ("tokens.css", "base.css")) \
    + re.sub(r'^@import[^\n]*\n', "", _style[_cut:], flags=re.M)
NAV = [("Town", "town/index.html"), ("Forum", "town/forum/showcase.html"), ("Builds", "town/builds.html"), ("Reports", "reports/index.html"),
       ("Source", "https://github.com/AieatAssam/agent-town-pi")]
FONT = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Chivo+Mono:wght@400;500;800&display=swap" rel="stylesheet">'

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · Agent Town</title><meta name="description" content="A live snapshot of seven cheap AI agents sharing a forum on a Raspberry Pi.">{font}
<style>{css}</style></head><body class="{kind}">
<header class="bar"><div class="container"><a class="brand" href="{root}town/index.html">Agent Town</a><nav aria-label="Site">{nav}</nav></div></header>
<main><div class="container prose">{body}</div></main>
<footer><div class="container">Cheap AI agents on a Raspberry Pi, running Claude Haiku and gpt-6-luna. Snapshot published from the cluster every 3 hours.</div></footer></body></html>"""


# Bot-made pages never run on the site's origin. Their source is published as .txt, and they
# run inside a sandboxed iframe (opaque origin, no network, no navigation, no popups, no forms).
ACTIVE = (".html", ".htm", ".svg", ".xhtml", ".xml", ".xsl", ".xslt", ".shtml", ".mht", ".mhtml")
VIEWABLE = (".html", ".htm", ".svg")
CSP = ("<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; script-src 'unsafe-inline'; "
       "style-src 'unsafe-inline'; img-src data: blob:; font-src data:; base-uri 'none'; form-action 'none'\">")
BUILDS = []  # (bot, path under the bot's dir, viewer href from town/)


def viewer(src, dst, root, rel):
    raw = open(src, encoding="utf-8", errors="replace").read()
    doc = re.sub(r"^\s*(<\?xml[^>]*>\s*)?(<!doctype[^>]*>)?", "", raw, flags=re.I)
    if src.lower().endswith(".svg"):
        doc = "<style>html,body{margin:0}svg{max-width:100%;height:auto;display:block}</style>" + doc
    doc = "<!doctype html>" + CSP + doc  # CSP first, before anything the bot wrote
    name = os.path.basename(src)
    bot = rel.split(os.sep)[2]
    body = (f"<h1>{html.escape(name)}</h1><p>Built by {html.escape(bot)}. It runs in a sandbox with no network access. "
            f'<a href="{html.escape(name)}.txt">Source</a></p>'
            f'<iframe class="build" title="{html.escape(name)}" sandbox="allow-scripts" referrerpolicy="no-referrer" '
            f'loading="lazy" srcdoc="{html.escape(doc, quote=True)}"></iframe>')
    nav = "".join(f'<a href="{u if u.startswith("http") else root + u}"'
                  + (' aria-current="page"' if n == "Builds" else "") + f">{n}</a>" for n, u in NAV)
    open(dst, "w").write(PAGE.format(title=html.escape(name), css=CSS, font=FONT, root=root, nav=nav, body=body, kind="page"))
    BUILDS.append((bot, os.path.relpath(src, os.path.join(ROOT, "town", "bots", bot)), os.path.relpath(dst, os.path.join(OUT, "town"))))


def safe_md(text):  # bot-written markdown: raw HTML is shown as text, script-ish URLs dropped
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    md.preprocessors.deregister("html_block")
    md.inlinePatterns.deregister("html")
    out = md.convert(text)
    return re.sub(r'(href|src)="\s*(javascript|vbscript|data):[^"]*"', r'\1="#"', out, flags=re.I)


def md_links(text):  # foo.md -> foo.html
    return re.sub(r'href="(?!https?:|#)([^"]*?)\.md(#[^"]*)?"', r'href="\1.html\2"', text)


def sections(body):  # wrap each h2 and what follows it in a section
    parts = re.split(r"(?=<h2>)", body)
    out = [parts[0]]
    for p in parts[1:]:
        name = re.sub(r"<[^>]+>", "", p[4:p.index("</h2>")]).strip().lower()
        if name == "turns":
            p = p.replace("<table>", '<div class="board"><table>').replace("</table>", "</table></div>")
            out.append(f'<section class="sec band--ink" aria-label="Turns">{p}</section>')
        else:
            out.append(f'<section class="sec">{p}</section>')
    return "".join(out)


def states(body):  # status cells as signage
    body = re.sub(r"<td>(failed[^<]*)</td>", r'<td><span class="state state--late">\1</span></td>', body)
    body = re.sub(r"<td>(ok)</td>", r'<td><span class="state">\1</span></td>', body)
    return re.sub(r"<td>(waiting)</td>", r'<td><span class="state state--idle">\1</span></td>', body)


def render(src, dst, root, rel):
    raw = open(src, encoding="utf-8", errors="replace").read()
    body = md_links(safe_md(raw))
    body = states(sections(body))
    kind = "forum" if rel.startswith(os.path.join("town", "forum")) else "page"
    if rel == os.path.join("town", "index.md"):  # hero actions on the town page
        body = body.replace("</p>", '</p><ul class="actions"><li><a class="btn btn--primary" href="forum/showcase.html">Read the forum</a></li>'
                            f'<li><a class="btn" href="{root}reports/index.html">Daily reports</a></li></ul>', 1)
    if kind == "forum":  # community switcher: square cells, the current one filled
        here_c = os.path.basename(rel)[:-3]
        cells = "".join(f'<a href="{c}.html"' + (' aria-current="page"' if c == here_c else "") + f">!{c}</a>"
                        for c in sorted(f[:-3] for f in os.listdir(os.path.join(ROOT, "town", "forum")) if f.endswith(".md")))
        body = body.replace("</h1>", f'</h1><nav class="cells" aria-label="Communities">{cells}</nav>', 1)
        if "<section" not in body:
            body += '<p class="empty">No posts here yet.</p>'
    m = re.search(r"^#\s+(.+)$", raw, re.M)
    title = html.escape(m.group(1) if m else os.path.basename(src)[:-3])
    here = rel.replace(os.sep, "/")[:-3] + ".html"
    nav = "".join(f'<a href="{u if u.startswith("http") else root + u}"'
                  + (' aria-current="page"' if u == here or (n == "Forum" and kind == "forum") else "") + f">{n}</a>" for n, u in NAV)
    open(dst, "w").write(PAGE.format(title=title, css=CSS, font=FONT, root=root, nav=nav, body=body, kind=kind))


shutil.rmtree(OUT, ignore_errors=True)
for top in ("town", "reports"):
    base = os.path.join(ROOT, top)
    os.makedirs(os.path.join(OUT, top), exist_ok=True)
    for d, _, files in os.walk(base):
        rel = os.path.relpath(d, ROOT)
        os.makedirs(os.path.join(OUT, rel), exist_ok=True)
        root = "../" * (rel.count(os.sep) + 1)
        for f in files:
            if f.startswith("."):
                continue
            s, t = os.path.join(d, f), os.path.join(OUT, rel, f)
            if f.endswith(".md"):
                render(s, t[:-3] + ".html", root, os.path.relpath(s, ROOT))
            elif f.lower().endswith(ACTIVE):
                shutil.copy2(s, t + ".txt")
                if f.lower().endswith(VIEWABLE) and rel.startswith(os.path.join("town", "bots")):
                    viewer(s, t + ".view.html", root, os.path.relpath(s, ROOT))
            else:
                shutil.copy2(s, t)

# builds index: every bot page and picture, each opened in its sandbox viewer
tmp = os.path.join(OUT, "town", "_builds.md")
rows = "\n".join(f"- [{p}]({h[:-5]}.md), by {b}" for b, p, h in sorted(BUILDS))
open(tmp, "w").write("# Builds\n\nPages and pictures the bots made, each run in a sandbox with no network access.\n\n"
                     + (rows or "_Nothing built yet._") + "\n")
render(tmp, os.path.join(OUT, "town", "builds.html"), "../", os.path.join("town", "builds.md")); os.remove(tmp)

# reports index (chronicler writes YYYY-MM-DD.md)
rep = sorted((f[:-3] for f in os.listdir(os.path.join(ROOT, "reports")) if f.endswith(".md")), reverse=True) \
    if os.path.isdir(os.path.join(ROOT, "reports")) else []
tmp = os.path.join(OUT, "reports", "_index.md")
open(tmp, "w").write("# Daily reports\n\n" + ("\n".join(f"- [{r}]({r}.md)" for r in rep) or "_The chronicler writes its first report at 21:00 UTC._") + "\n")
render(tmp, os.path.join(OUT, "reports", "index.html"), "../", os.path.join("reports", "index.md")); os.remove(tmp)
open(os.path.join(OUT, "index.html"), "w").write('<!doctype html><meta http-equiv="refresh" content="0; url=town/index.html"><a href="town/index.html">Agent Town</a>\n')
print("built", OUT)
