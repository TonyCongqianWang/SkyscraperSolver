"""Smoke tests for the work-calibration fit; no external dependencies."""
import importlib.util
from pathlib import Path
import unittest
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / "calibrate_work.py"
spec = importlib.util.spec_from_file_location("calibrate_work", SCRIPT)
calibration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calibration)


class CalibrationModelTests(unittest.TestCase):
    def test_compiled_modes_preserve_determinism(self):
        puzzles = calibration.read_puzzles(
            ["benchmark_sets/benchmarkSet7_easy500.txt"], 1)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            variant = {"name": "baseline", "parameters": {}}
            instrumented, _ = calibration.build(
                directory, variant, True, "gcc", [])
            native, _ = calibration.build(
                directory, variant, False, "gcc", [])
            first = calibration.execute(instrumented, puzzles[0], 1, 30)
            second = calibration.execute(instrumented, puzzles[0], 1, 30)
            ordinary = calibration.execute(native, puzzles[0], 1, 30)
            self.assertEqual(first[1:], second[1:])
            self.assertEqual(first[1:3], ordinary[1:3])
            self.assertIsNotNone(first[3])
            self.assertIsNone(ordinary[3])

    def test_nonnegative_fit(self):
        samples = []
        for a, b in [(0, 1), (1, 1), (2, 2), (3, 0), (4, 3), (7, 1)]:
            samples.append({
                "counters": {"setup_cell": a, "cache_pair_copy": b},
                "runtime_median_seconds": 0.3 + 0.2 * a + 0.1 * b,
            })
        model = calibration.fit_nonnegative(
            samples, ("setup_cell", "cache_pair_copy"))
        for name, weight in model["seconds_per_count"].items():
            self.assertGreaterEqual(weight, 0.0, name)
        self.assertAlmostEqual(model["intercept_seconds"], 0.3, places=5)
        self.assertAlmostEqual(model["seconds_per_count"]["setup_cell"], 0.2, places=5)
        self.assertAlmostEqual(model["seconds_per_count"]["cache_pair_copy"], 0.1, places=5)

    def test_split_keeps_configuration_variants_together(self):
        rows = []
        for line in range(10):
            for configuration in ("baseline", "variant"):
                rows.append({"dataset": "one", "line": line,
                             "configuration": configuration})
        train, validation = calibration.split(rows, 0.3, 72)
        train_ids = {(r["dataset"], r["line"]) for r in train}
        val_ids = {(r["dataset"], r["line"]) for r in validation}
        self.assertFalse(train_ids & val_ids)
        self.assertEqual(len(val_ids), 3)

    def test_metric_ranking_uses_same_puzzle(self):
        coefficients = {"intercept_seconds": 0.0,
                        "seconds_per_count": {"setup_cell": 0.5}}
        rows = [{"dataset": "one", "line": 1, "configuration": config,
                 "runtime_median_seconds": runtime,
                 "counters": {"setup_cell": count}}
                for config, runtime, count in
                [("baseline", 1.0, 2), ("variant", 2.0, 4)]]
        metrics = calibration.diagnostics(rows, coefficients)
        self.assertEqual(metrics["ranking_pairs"], 1)
        self.assertEqual(metrics["ranking_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
