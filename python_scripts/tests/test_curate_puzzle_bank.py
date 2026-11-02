"""Curated bank difficulty boundaries and per-band sampling tests."""
import json
import tempfile
import unittest
from pathlib import Path

from python_scripts.puzzle_bank.curate import curate_size, difficulty


class CuratorTests(unittest.TestCase):
    def test_main_node_override(self):
        self.assertEqual(difficulty(100, 1), "very_easy")
        self.assertEqual(difficulty(101, 1), "easy")
        self.assertEqual(difficulty(200, 1), "easy")
        self.assertEqual(difficulty(400, 1), "medium")
        self.assertEqual(difficulty(800, 1), "hard")
        self.assertEqual(difficulty(1600, 1), "very_hard")
        self.assertEqual(difficulty(99999, 1), "very_hard")
        self.assertEqual(difficulty(20, 2), "hard")
        self.assertEqual(difficulty(5000, 2), "very_hard")
        self.assertEqual(difficulty(200, 3), "hard")
        self.assertEqual(difficulty(1600, 8), "very_hard")
        self.assertEqual(difficulty(3200, 8), "extreme")
        self.assertEqual(difficulty(50, 9), "impossible")

    def test_reservoir_cap_and_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "candidates.json"
            out = Path(td) / "curated"
            variants = [
                {"label": f"clues_plus_{j}_1", "clues": [j] * 16,
                 "givens": [0] * 16, "clue_count": 16,
                 "nodes_visited": 100, "main_nodes_visited": 1}
                for j in range(1, 6)
            ]
            bank = {"size": 4, "groups": [{
                "id": "solution_1", "canonical_solution": list(range(16)),
                "puzzles": [{"id": "minimal_1", "variants": variants}]
            }]}
            src.write_text(json.dumps(bank))
            info = curate_size(src, out, 2, 123)
            self.assertEqual(info["statistics"]["very_easy"]["available"], 5)
            self.assertEqual(info["statistics"]["very_easy"]["selected"], 2)
            result = json.loads((out / "size_4.json").read_text())
            self.assertEqual(len(result["difficulties"]["very_easy"]), 2)
            for v in result["difficulties"]["very_easy"]:
                self.assertEqual(v["minimal_puzzle_id"], "minimal_1")
                self.assertEqual(v["solution_group_id"], "solution_1")


if __name__ == "__main__":
    unittest.main()
