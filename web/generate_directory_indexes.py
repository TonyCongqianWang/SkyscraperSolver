#!/usr/bin/env python3
"""Generate old-style directory listings for the staged, static puzzle bank."""
from html import escape
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public/puzzle-bank")
if not root.is_dir():
    raise SystemExit(f"Not a directory: {root}")

for directory in sorted([root, *root.rglob("*")]):
    if not directory.is_dir():
        continue
    entries = sorted(
        (p for p in directory.iterdir() if p.name != "index.html" and not p.name.startswith(".")),
        key=lambda p: (not p.is_dir(), p.name)
    )
    relative = directory.relative_to(root)
    url_path = "/puzzle-bank/" + (str(relative).replace("\\", "/").strip("/") + "/" if relative.parts else "")
    links = ['<a href="../">../</a>'] if directory != root else ['<a href="../">../</a>']
    for item in entries:
        name = item.name + ("/" if item.is_dir() else "")
        links.append(f'<a href="{escape(name, quote=True)}">{escape(name)}</a>')
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Index of {escape(url_path)}</title>'
        '<style>body{font:15px/1.5 monospace;max-width:900px;margin:2em auto;padding:0 1em}'
        'h1{font-size:1.5em;font-weight:normal}a{color:#00e}a:visited{color:#551a8b}'
        'hr{border:0;border-top:1px solid #999}pre{font:inherit}</style>'
        '</head><body>'
        f'<h1>Index of {escape(url_path)}</h1><hr><pre>'
        + "\n".join(links) +
        '</pre><hr><p>Raw puzzle-bank JSON files for API use.</p></body></html>\n'
    )
    (directory / "index.html").write_text(page, encoding="utf-8")
    print(f"Indexed {url_path}: {len(entries)} entries")
