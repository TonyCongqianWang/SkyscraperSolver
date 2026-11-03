"""Small fixture checks for the static website registry and curated exporter."""
import json
import tempfile
import unittest
from pathlib import Path

from python_scripts.puzzle_bank.export_api_metadata import LEVELS, export_curated
from web.endpoint_registry import EndpointRegistry


class StaticAssetsTests(unittest.TestCase):
    def test_shards_and_statistics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, destination = root / "input", root / "output"
            source.mkdir()
            for size in range(4, 10):
                buckets = {level: [] for level in LEVELS}
                if size in (4, 7):
                    level = "easy" if size == 4 else "extreme_plus"
                    buckets[level] = [
                        {"id": "a", "clues": [0] * (4 * size),
                         "givens": [0] * (size * size),
                         "canonical_solution": [1] * (size * size),
                         "nodes_visited": 10, "main_nodes_visited": 1,
                         "clue_count": 0, "given_count": 0},
                        {"id": "b", "clues": [1] * (4 * size),
                         "givens": [1] * (size * size),
                         "canonical_solution": [1] * (size * size),
                         "nodes_visited": 30, "main_nodes_visited": 3,
                         "clue_count": 4 * size, "given_count": size * size},
                    ]
                bank = {"schema_version": 1, "size": size,
                        "curated_version": "v2", "source_bank": "unique/v3/minimal",
                        "difficulty_policy": "main_node_override_v2",
                        "quotas": {level: 0 for level in LEVELS},
                        "difficulties": buckets}
                (source / f"size_{size}.json").write_text(json.dumps(bank))
            metadata, stats = export_curated(source, destination)
            self.assertEqual(metadata["sizes"]["4"]["easy"], 2)
            self.assertEqual(metadata["sizes"]["7"]["extreme_plus"], 2)
            self.assertFalse((destination / "4" / "hard.json").exists())
            shard = json.loads((destination / "7" / "extreme_plus.json").read_text())
            self.assertEqual(shard["curated_version"], "v1")
            self.assertEqual(shard["source_bank"], "unique/v1/minimal")
            self.assertEqual(shard["puzzles"][0]["id"], "a")
            dist = stats["details"]["4"]["easy"]["metrics"]["nodes_visited"]
            self.assertEqual(dist["p50"], 20)
            self.assertEqual(dist["min"], 10)
            self.assertEqual(dist["max"], 30)
            self.assertEqual(sum(dist["histogram"]), 2)
            self.assertEqual(stats["details"]["all"]["easy"]["count"], 2)
            self.assertEqual(stats["details"]["7"]["extreme_plus"]["metrics"]["given_count"]["max"], 49)

    def test_registry_generates_nested_indexes_and_catalog(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "puzzle.json"
            source.write_text('{"ok":true}')
            site = EndpointRegistry(root / "public")
            site.add_page("/", None, "Home")
            site.add_asset("/assets/index.json", description="Catalog", kind="json")
            site.add_asset("/assets/puzzles/curated/v1/4/easy.json", source,
                           "4x4 easy", kind="json")
            with self.assertRaises(ValueError):
                site.add_asset("/assets/puzzles/curated/v1/4/easy.json", source)
            with self.assertRaises(ValueError):
                site.add_asset("/assets/puzzles/../other.json", source)
            catalog = site.build()
            self.assertEqual(len(catalog["endpoints"]), 2)
            for path in ("index.html", "assets/index.html", "assets/puzzles/index.html",
                         "assets/puzzles/curated/v1/4/index.html",
                         "assets/index.json", "assets/puzzles/curated/v1/4/easy.json"):
                self.assertTrue((root / "public" / path).is_file(), path)
            self.assertIn("easy.json", (root / "public/assets/puzzles/curated/v1/4/index.html").read_text())
            self.assertEqual(json.loads((root / "public/assets/index.json").read_text())["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
