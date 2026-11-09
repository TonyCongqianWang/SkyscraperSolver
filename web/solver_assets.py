"""Register the default solver and any published release variants."""
import json


def register_solver_assets(site, output):
    manifest_path = output / "assets/solver/versions.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        # Local builds and PR previews compile the current checkout.
        manifest = {"default": "development", "versions": [
            {"id": "development", "tag": "Development build",
             "prerelease": False, "path": "solver.js"}
        ]}
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    versions = manifest["versions"]
    if not versions or manifest["default"] not in {v["id"] for v in versions}:
        raise ValueError("Missing default solver version")
    site.add_asset("/assets/solver/versions.json", description="Available solver versions", kind="json")
    loaders = {"solver.js"}
    for version in versions:
        if version["path"] not in ("solver.js", "release/solver.js", "prerelease/solver.js"):
            raise ValueError("Unsupported solver path")
        loaders.add(version["path"])
    for loader in sorted(loaders):
        site.add_asset(f"/assets/solver/{loader}", description="WebAssembly solver loader", kind="javascript")
        site.add_asset(f"/assets/solver/{loader[:-3]}.wasm", description="Compiled WebAssembly solver", kind="wasm")
