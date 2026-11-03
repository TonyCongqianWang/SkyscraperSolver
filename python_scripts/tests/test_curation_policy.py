"""Regression checks for difficulty grading and curation minima."""
import unittest
from python_scripts.puzzle_bank.curate import LEVELS, difficulty

class CurationPolicyTests(unittest.TestCase):
    def test_main_one_thresholds(self):
        for nodes, level in [(50,"very_easy"), (51,"easy"), (100,"easy"),
                             (101,"medium"), (200,"medium"), (201,"hard"),
                             (400,"hard"), (401,"very_hard")]:
            self.assertEqual(difficulty(nodes, 1), level)

    def test_main_node_restrictions_unchanged(self):
        self.assertEqual(difficulty(400, 2), "hard")
        self.assertEqual(difficulty(401, 2), "very_hard")
        self.assertEqual(difficulty(400, 3), "hard")
        self.assertEqual(difficulty(800, 8), "very_hard")
        self.assertEqual(difficulty(1600, 3), "extreme")
        self.assertEqual(difficulty(1601, 3), "extreme")
        self.assertEqual(difficulty(3201, 4), "extreme")
        self.assertEqual(difficulty(1601, 5), "extreme_plus")
        self.assertEqual(difficulty(3201, 5), "extreme_plus_plus")
        self.assertEqual(difficulty(1, 9), "hard")
        self.assertEqual(difficulty(1601, 9), "extreme_plus")

    def test_levels(self):
        self.assertEqual(LEVELS[-2:], ("extreme_plus", "impossible"))

if __name__ == "__main__":
    unittest.main()
