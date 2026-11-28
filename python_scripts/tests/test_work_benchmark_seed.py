import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmark_work_calibration import resolve_seed, training_overlap
from unittest.mock import patch


class BenchmarkSeedTests(unittest.TestCase):
    def test_saved_seed_is_exact(self):
        self.assertEqual(resolve_seed({"calibration_seed": "18446744073709551615"}),
                         18446744073709551615)

    def test_cli_overrides_saved_seed(self):
        self.assertEqual(resolve_seed({"calibration_seed": "123"}, 0), 0)

    def test_legacy_model_requires_seed(self):
        with self.assertRaisesRegex(ValueError, "--seed"):
            resolve_seed({})

    def test_legacy_model_accepts_cli(self):
        self.assertEqual(resolve_seed({}, 42), 42)

    def test_training_overlap_is_model_specific(self):
        model = {"calibration_seed": "123", "calibration_puzzles_per_size": 2,
                 "calibration_validation_fraction": .5, "dataset_sha256": {"bank": "abc"}}
        def puzzle(identity):
            return {"size": 7, "identity": identity, "dataset": "bank", "dataset_sha256": "abc"}
        selected = [puzzle("a"), puzzle("b"), puzzle("c")]
        with patch("benchmark_work_calibration.original_split",
                   return_value=([puzzle("a")], [puzzle("b")])):
            overlap, independent = training_overlap(model, selected)
        self.assertEqual(overlap["status"], "overlap")
        self.assertEqual(overlap["training_puzzles"], 1)
        self.assertEqual(independent, {(7, "b"), (7, "c")})

    def test_legacy_or_changed_dataset_overlap_is_unknown(self):
        self.assertIsNone(training_overlap({}, [])[1])
        model = {"calibration_seed": "123", "calibration_puzzles_per_size": 2,
                 "calibration_validation_fraction": .5, "dataset_sha256": {"bank": "abc"}}
        with patch("benchmark_work_calibration.original_split",
                   return_value=([{"dataset": "bank", "dataset_sha256": "changed"}], [])):
            overlap, independent = training_overlap(model, [])
        self.assertEqual(overlap["status"], "unknown")
        self.assertIsNone(independent)
