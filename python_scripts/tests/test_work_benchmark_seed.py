import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmark_work_calibration import resolve_seed


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
