"""Retry behavior for direct curation from minimal puzzles."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from python_scripts.puzzle_bank import fill_curated


class RetryTests(unittest.TestCase):
    def test_revisits_pool_and_stops_after_1000_nonprogress_draws(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "minimal.json"
            target = Path(temp) / "curated.json"
            grid = [1, 2, 3, 4] * 4
            source.write_text(json.dumps({
                "size": 4, "groups": [{
                    "id": "g1", "canonical_solution": grid,
                    "puzzles": [{"id": "p1", "clues": [0]*16,
                                 "givens": [0]*16}]
                }]
            }))
            calls = []
            def fake_verify(*args):
                calls.append(1)
                return (1, 20, 1)
            quotas = {name: 0 for name in fill_curated.LEVELS}
            quotas["easy"] = 1  # Unreachable with fake verification.
            with patch.object(fill_curated, "verify", side_effect=fake_verify), \
                 patch.object(fill_curated, "clues_for", return_value=[1]*16):
                stats = fill_curated.fill_size(
                    4, quotas, source, target, None, 1, 123, 2)
            self.assertEqual(stats["easy"]["selected"], 0)
            self.assertEqual(stats["very_easy"]["selected"], len(
                json.loads(target.read_text())["difficulties"]["very_easy"]))
            self.assertLessEqual(len(calls), 1000)
            self.assertGreater(len(calls), 2)

if __name__ == "__main__":
    unittest.main()
