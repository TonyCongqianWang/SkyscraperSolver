#!/usr/bin/env python3
"""Register static endpoints and build navigable indexes with a shared catalog."""
from dataclasses import dataclass, field
from html import escape
import json
from pathlib import Path
import shutil


@dataclass
class Node:
    name: str
    path: str
    directory: bool = True
    description: str = ""
    kind: str = "directory"
    source: Path | None = None
    children: dict = field(default_factory=dict)
    page: Path | None = None


class EndpointRegistry:
    def __init__(self, output):
        self.output = Path(output)
        self.root = Node("", "/")

    def _register(self, route, directory, description, kind, source):
        if not route.startswith("/") or (directory != route.endswith("/")):
            raise ValueError(f"Invalid endpoint route: {route}")
        parts = route.strip("/").split("/") if route != "/" else []
        if any(part in ("", ".", "..") for part in parts):
            raise ValueError(f"Unsafe endpoint route: {route}")
        node = self.root
        for index, part in enumerate(parts):
            final = index == len(parts) - 1
            is_dir = directory if final else True
            path = "/" + "/".join(parts[:index + 1]) + ("/" if is_dir else "")
            child = node.children.get(part)
            if child is None:
                child = Node(part, path, directory=is_dir, kind="directory" if is_dir else kind)
                node.children[part] = child
            elif child.directory != is_dir:
                raise ValueError(f"Endpoint collision: {route}")
            elif final and (child.source is not None or child.page is not None or child.description):
                raise ValueError(f"Duplicate endpoint: {route}")
            node = child
        node.description = description
        node.kind = kind
        if directory:
            node.page = Path(source) if source else None
        else:
            node.source = Path(source) if source else None
        return node

    def add_page(self, route, source, description=""):
        return self._register(route, True, description, "page", source)

    def add_directory(self, route, description=""):
        """Describe a generated directory index without replacing its listing."""
        return self._register(route, True, description, "directory", None)

    def add_asset(self, route, source=None, description="", kind="asset"):
        return self._register(route, False, description, kind, source)

    def _walk(self, node=None):
        node = self.root if node is None else node
        yield node
        for child in node.children.values():
            yield from self._walk(child)

    def _target(self, node):
        return self.output / node.path.lstrip("/")

    @staticmethod
    def _index(node):
        title = "Index of " + node.path
        links = ['<a href="../">../</a>'] if node.path != "/" else []
        for child in sorted(node.children.values(), key=lambda x: (not x.directory, x.name)):
            name = child.name + ("/" if child.directory else "")
            desc = ("  " + child.description) if child.description else ""
            links.append(f'<a href="{escape(name, quote=True)}">{escape(name)}</a>{escape(desc)}')
        return (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title><style>'
            'body{max-width:900px;margin:2em auto;padding:0 1em;background:#fff;'
            'color:#111;font:15px/1.5 monospace}'
            'h1{font-size:1.5em;font-weight:normal}a{color:#00e}'
            'a:visited{color:#551a8b}hr{border:0;border-top:1px solid #999}'
            'pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere}'
            '</style></head><body>'
            f'<h1>{escape(title)}</h1>'
            + (f'<p>{escape(node.description)}</p>' if node.description else "")
            + '<hr><pre>' + "\n".join(links) + '</pre><hr></body></html>\n'
        )

    @staticmethod
    def _tree(node):
        return {
            "path": node.path, "type": "directory" if node.directory else node.kind,
            "description": node.description,
            **({"children": [EndpointRegistry._tree(child)
                 for child in sorted(node.children.values(), key=lambda x: x.name)]}
               if node.directory else {}),
        }

    def build(self):
        nodes = list(self._walk())
        for node in nodes:
            if node.directory:
                self._target(node).mkdir(parents=True, exist_ok=True)
            elif node.source is not None:
                target = self._target(node)
                target.parent.mkdir(parents=True, exist_ok=True)
                if node.source.resolve() != target.resolve():
                    shutil.copyfile(node.source, target)

        assets = self.root.children.get("assets")
        if assets is None or not assets.directory:
            raise ValueError("Missing /assets/ index")
        catalog = {
            "schema_version": 1,
            "base_path": "assets/",
            "tree": self._tree(assets),
            "endpoints": [
                {"path": node.path, "type": node.kind, "description": node.description}
                for node in nodes if node.path.startswith("/assets/") and not node.directory
            ],
        }
        catalog_path = self.output / "assets/index.json"
        catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

        for node in nodes:
            target = self._target(node)
            if node.directory:
                index = target / "index.html"
                if node.page:
                    shutil.copyfile(node.page, index)
                else:
                    index.write_text(self._index(node), encoding="utf-8")
            elif not target.is_file():
                raise FileNotFoundError(f"Unstaged asset: {node.path}")
        (self.output / ".nojekyll").touch()
        return catalog
