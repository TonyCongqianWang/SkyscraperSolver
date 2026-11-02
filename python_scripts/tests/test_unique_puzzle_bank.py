"""Small deterministic checks for the v2 puzzle-bank logic (no native solver)."""
import unittest
from unittest.mock import patch

from python_scripts.puzzle_bank import generate_unique as bank


class PuzzleBankTests(unittest.TestCase):
    def setUp(self):
        self.square = [[1, 2, 3, 4], [2, 3, 4, 1],
                       [3, 4, 1, 2], [4, 1, 2, 3]]

    def test_shared_mcmc_sampler_reseeds(self):
        from python_scripts.dataset_generation.generator import MCMCLatinSquareSampler
        sampler = MCMCLatinSquareSampler(4, seed=42, burn_in=1,
                                         gap=1, batch_size=2)
        a = sampler.next_square()
        self.assertEqual(a.shape, (4, 4))
        self.assertEqual(set(a[0].tolist()), {1, 2, 3, 4})
        sampler.reseed()
        b = sampler.next_square()
        self.assertEqual(set(b[0].tolist()), {1, 2, 3, 4})
        self.assertEqual(sampler.next_burn_in, 0)

    def test_d4_canonical_representative(self):
        key = bank.solution_key(self.square)
        for transformed in bank.square_symmetries(self.square):
            self.assertEqual(bank.solution_key(transformed), key)
        self.assertEqual(len(key), 16)
        self.assertEqual(set(key), {1, 2, 3, 4})

    def test_d4_does_not_identify_value_relabeling(self):
        # Rotations and reflections are geometric symmetries;
        # arbitrary height changes must not be normalized away.
        original = bank.solution_key(self.square)
        relabeled = [[5 - v for v in row] for row in self.square]
        self.assertNotEqual(original, bank.solution_key(relabeled))

    def test_variants_are_distinct_and_limited(self):
        grid = self.square
        clues = [0] * 16
        full = bank.clues_for(grid)
        cells = [0] * 16
        def verify(_binary, clue_values, grid_values, _timeout, **kwargs):
            return (1, sum(bool(v) for v in clue_values) * 7 + sum(bool(v) for v in grid_values),\n                    sum(bool(v) for v in clue_values))

        with patch.object(bank, "verify", side_effect=verify):
            variants = bank.generate_variants(
                None, "test", clues, cells, full, grid, (1, 1),
                __import__("random").Random(123), 1, 123, 1, 4)

        # One baseline, four samples for each clue count 1..15,
        # one full clue set, four samples for each added given 1..5.
        self.assertEqual(len(variants), 1 + 4 * 15 + 1 + 4 * 5)
        self.assertEqual(sum(v["label"] == "full_clues" for v in variants), 1)
        self.assertEqual(len({
            (tuple(v["clues"]), tuple(v["givens"])) for v in variants
        }), len(variants))
        self.assertTrue(all(v["given_count"] <= 16 // 3 for v in variants))\n        self.assertTrue(all("main_nodes_visited" in v for v in variants))


if __name__ == "__main__":
    unittest.main()
