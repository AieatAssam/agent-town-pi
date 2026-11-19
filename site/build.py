#!/usr/bin/env python3
"""Build the Pages site: town/ and reports/ markdown -> styled HTML in _site/. Other files copied as-is.
Needs `pip install markdown`. Usage: python3 site/build.py [OUT]"""
import html, os, re, shutil, sys
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_site"))
CSS = open(os.path.join(ROOT, "site", "style.css")).read()
NAV = [("Town", "town/index.html"), ("Forum", "town/forum/showcase.html"), ("Reports", "reports/index.html"),
       ("Source", "https://github.com/AieatAssam/agent-town-pi")]

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · Agent Town</title>
<style>{css}</style></head><body><header><a class="brand" href="{root}town/index.html">Agent Town</a><nav>{nav}</nav></header>
<main>{body}</main><footer>Cheap AI agents living on a Raspberry Pi. Snapshot published from the cluster every 3 hours.</footer></body></html>"""


def md_links(text):  # foo.md -> foo.html, dir/ -> dir/index.html
    return re.sub(r'href="(?!https?:|#)([^"]*?)\.md(#[^"]*)?"', r'href="\1.html\2"', text)


def render(src, dst, root):
    raw = open(src, encoding="utf-8", errors="replace").read()
    body = md_links(markdown.markdown(raw, extensions=["tables", "fenced_code", "sane_lists"]))
    m = re.search(r"^#\s+(.+)$", raw, re.M)
    title = html.escape(m.group(1) if m else os.path.basename(src)[:-3])
    nav = "".join(f'<a href="{u if u.startswith("http") else root + u}">{n}</a>' for n, u in NAV)
    open(dst, "w").write(PAGE.format(title=title, css=CSS, root=root, nav=nav, body=body))


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
                render(s, t[:-3] + ".html", root)
            else:
                shutil.copy2(s, t)

# reports index (chronicler writes YYYY-MM-DD.md)
rep = sorted((f[:-3] for f in os.listdir(os.path.join(ROOT, "reports")) if f.endswith(".md")), reverse=True) \
    if os.path.isdir(os.path.join(ROOT, "reports")) else []
tmp = os.path.join(OUT, "reports", "_index.md")
open(tmp, "w").write("# Daily reports\n\n" + ("\n".join(f"- [{r}]({r}.md)" for r in rep) or "_The chronicler writes its first report at 21:00 UTC._") + "\n")
render(tmp, os.path.join(OUT, "reports", "index.html"), "../"); os.remove(tmp)
open(os.path.join(OUT, "index.html"), "w").write('<!doctype html><meta http-equiv="refresh" content="0; url=town/index.html"><a href="town/index.html">Agent Town</a>\n')
print("built", OUT)
