#!/usr/bin/env python3
"""Build the complete static website from the current v1 puzzle banks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python_scripts.puzzle_bank.export_api_metadata import LEVELS, export_curated
from endpoint_registry import EndpointRegistry
from solver_assets import register_solver_assets


def build_site(output):
    output = Path(output)
    site = EndpointRegistry(output)
    site.add_page("/", ROOT / "web/home.html", "Homepage")
    site.add_page("/demo/", ROOT / "web/index.html", "WebAssembly solver demo")
    site.add_page("/curated/", ROOT / "web/curated.html", "Curated explorer")

    site.add_asset("/assets/index.json", description="Machine-readable endpoint catalog", kind="json")
    site.add_directory(
        "/assets/solver/", footer=ROOT / "web/solver-description.html"
    )
    register_solver_assets(site, output)
    site.add_asset("/assets/solver/worker.js", ROOT / "web/worker.js",
                   "Worker used by the solver demo", "javascript")
    site.add_asset("/assets/puzzles/puzzles.js", ROOT / "web/puzzles.js",
                   "Client-side random curated puzzle API", "javascript")

    for size in range(4, 10):
        source = ROOT / f"puzzle_bank/unique/v1/minimal/size_{size}.json"
        try:
            bank = json.loads(source.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise ValueError(f"Unavailable unique puzzle bank: {source}") from exc
        if bank.get("size") != size or not isinstance(bank.get("groups"), list):
            raise ValueError(f"Incorrect unique puzzle bank: {source}")
        site.add_asset(
            f"/assets/puzzles/unique/v1/minimal/size_{size}.json", source,
            f"Unique minimal {size}x{size} puzzles", "json",
        )

    dest = output / "assets/puzzles/curated/v1"
    metadata, _ = export_curated(ROOT / "puzzle_bank/curated/v1", dest)
    site.add_asset("/assets/puzzles/curated/v1/metadata.json",
                   description="Available counts by size and difficulty", kind="json")
    site.add_asset("/assets/puzzles/curated/v1/statistics.json",
                   description="Percentiles and distribution histograms", kind="json")
    for size, counts in metadata["sizes"].items():
        for level in LEVELS:
            if counts[level]:
                site.add_asset(
                    f"/assets/puzzles/curated/v1/{size}/{level}.json",
                    description=f"{size}x{size} {level} curated puzzles ({counts[level]})",
                    kind="json",
                )
    return site.build()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "public")
    args = parser.parse_args()
    build_site(args.output)
