"""Direct-from-minimal curated filling smoke tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from python_scripts.puzzle_bank.curate import LEVELS
from python_scripts.puzzle_bank.fill_curated import fill_size


class DirectCurationTests(unittest.TestCase):
    def test_zero_quotas_do_not_call_solver(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal = root / "minimal.json"
            minimal.write_text(json.dumps({
                "size": 4,
                "groups": [{"id": "g1", "canonical_solution": [
                    1, 2, 3, 4, 2, 3, 4, 1,
                    3, 4, 1, 2, 4, 1, 2, 3],
                    "puzzles": [{"id": "m1", "clues": [0]*16,
                                 "givens": [0]*16}]}]
            }))
            out = root / "curated.json"
            with patch("python_scripts.puzzle_bank.fill_curated.verify") as verify:
                counts = fill_size(4, {k: 0 for k in LEVELS}, minimal, out,
                                   root / "unused_solver", 1, 42, 10)
                verify.assert_not_called()
            self.assertEqual(counts["very_easy"]["selected"], 0)
            self.assertTrue(out.exists())

    def test_cartesian_samples_keep_minimal_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal = root / "minimal.json"
            minimal.write_text(json.dumps({
                "size": 4,
                "groups": [{"id": "g1", "canonical_solution": [
                    1, 2, 3, 4, 2, 3, 4, 1,
                    3, 4, 1, 2, 4, 1, 2, 3],
                    "puzzles": [{"id": "m1", "clues": [0]*16,
                                 "givens": [0]*16}]}]
            }))
            out = root / "curated.json"
            quota = {k: 0 for k in LEVELS}
            quota["very_easy"] = 2
            with patch("python_scripts.puzzle_bank.fill_curated.verify",
                       return_value=(1, 40, 1)):
                counts = fill_size(4, quota, minimal, out, None, 1, 42, 20)
            self.assertEqual(counts["very_easy"]["selected"], 2)
            entries = json.loads(out.read_text())["difficulties"]["very_easy"]
            self.assertTrue(all(v["minimal_puzzle_id"] == "m1" for v in entries))
            self.assertTrue(all(v["solution_group_id"] == "g1" for v in entries))


if __name__ == "__main__":
    unittest.main()
