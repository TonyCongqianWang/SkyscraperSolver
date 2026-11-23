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
            ["puzzle_bank/spsa_datasets/size8_train.txt"], 1)
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
            self.assertEqual(calibration.SCHEMA, "v1")
            counts = first[3]
            self.assertEqual(
                counts["line_score_value"],
                counts["line_score"] * puzzles[0]["size"])
            self.assertEqual(
                counts["index_copy_pair"],
                counts["index_copy_call"] * puzzles[0]["size"])
            self.assertEqual(
                counts["dp_init_write"],
                counts["dp_init_call"]
                * (4 * (puzzles[0]["size"] + 1) ** 2 + 2
                   + 2 * (puzzles[0]["size"] + 1)))

    def test_work_counter_names_describe_current_operations(self):
        from tuning_work_runtime import DEFAULT_MODEL
        actual = set(calibration.COUNTER_NAMES)
        self.assertIn("dp_candidate_check", actual)
        self.assertIn("cache_build_candidate", actual)
        self.assertIn("provisional_solution_rollback", actual)
        self.assertFalse({"gac_check", "cache_build_check", "rollback"} & actual)
        self.assertEqual(DEFAULT_MODEL.name, "work_calibration.model.json")
        self.assertEqual(len(actual), 48)

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

    def test_ridge_shrinks_coefficients_without_penalizing_intercept(self):
        data = [{"counters": {"setup_cell": n},
                 "runtime_median_seconds": 2.0 + n}
                for n in (0, 1, 2, 3)]
        ordinary = calibration.fit_nonnegative(data, ["setup_cell"])
        regularized = calibration.fit_nonnegative(
            data, ["setup_cell"], ridge_alpha=100)
        self.assertAlmostEqual(ordinary["intercept_seconds"], 2.0, places=5)
        self.assertLess(
            regularized["seconds_per_count"]["setup_cell"],
            ordinary["seconds_per_count"]["setup_cell"])
        self.assertGreater(regularized["intercept_seconds"], 2.0)
        self.assertEqual(ordinary["ridge_alpha"], 0.0)

    def test_contrast_penalty_changes_configuration_sensitivity(self):
        rows = []
        for puzzle, base in (("one", 0), ("two", 10)):
            for i in range(2):
                rows.append({
                    "identity": puzzle,
                    "counters": {"setup_cell": base + i},
                    "runtime_median_seconds":
                        (100.0 if puzzle == "two" else 0.0) + 0.1 * i,
                })
        plain = calibration.fit_nonnegative(rows, ["setup_cell"])
        contrasted = calibration.fit_nonnegative(
            rows, ["setup_cell"], contrast_weight=200)
        self.assertLess(
            contrasted["seconds_per_count"]["setup_cell"],
            plain["seconds_per_count"]["setup_cell"])

    def test_confident_ranking_filters_small_noisy_deltas(self):
        from work_ranking import ranking_diagnostics
        rows = []
        for name, observed, count in (
                ("base", 1.0, 0), ("near", 1.00001, 3),
                ("clear", 1.01, 10)):
            rows.append({
                "dataset": "fixture", "identity": "one", "size": 8,
                "configuration": name, "max_solutions": 1,
                "runtime_median_seconds": observed,
                "native_times_seconds": [
                    observed - 0.001, observed, observed + 0.001],
                "counters": {"setup_cell": count},
            })
        result = ranking_diagnostics(
            rows, lambda row: row["counters"]["setup_cell"] / 1000)
        self.assertEqual(result["ranking_pairs"], 3)
        self.assertEqual(result["clear_ranking_pairs"], 2)
        self.assertEqual(result["noise_excluded_pairs"], 1)
        self.assertEqual(result["clear_ranking_accuracy"], 1.0)
        self.assertIsNotNone(result["within_puzzle_r2"])

    def test_hyperparameter_selection_uses_only_inner_training(self):
        rows = []
        for index in range(12):
            for variant in (0, 1, 2):
                counts = {name: 0 for name in calibration.COUNTER_NAMES}
                counts["base_score"] = index ** 2 + variant
                counts["cache_pair_copy"] = index + 3 * variant
                rows.append({
                    "identity": str(index), "dataset": "fixture",
                    "line": index, "size": 8,
                    "configuration": str(variant),
                    "counters": counts,
                    "runtime_median_seconds":
                        0.02 + 0.00002 * counts["base_score"]
                        + 0.00001 * counts["cache_pair_copy"],
                    "native_times_seconds": [0.01, 0.011, 0.009],
                })
        choice = calibration.choose_regularization(
            rows, 0.995, 1e-3, (0.0, 0.0001), (0.0, 2.0), 72)
        self.assertEqual(len(choice["candidates"]), 4)
        self.assertLess(choice["inner_training_samples"], len(rows))
        self.assertGreater(choice["inner_validation_samples"], 0)
        self.assertIn(choice["ridge_alpha"], (0.0, 0.0001))
        self.assertIn(choice["contrast_weight"], (0.0, 2.0))

    def test_split_keeps_configuration_variants_together(self):
        rows = []
        for line in range(10):
            for configuration in ("baseline", "variant"):
                rows.append({"dataset": "one", "line": line, "size": 7,
                             "identity": str(line), "configuration": configuration})
        train, validation = calibration.split(rows, 0.3, 72)
        train_ids = {(r["dataset"], r["line"]) for r in train}
        val_ids = {(r["dataset"], r["line"]) for r in validation}
        self.assertFalse(train_ids & val_ids)
        self.assertEqual(len(val_ids), 3)

    def test_default_dataset_targets(self):
        self.assertEqual(
            calibration.DEFAULT_DATASETS,
            ("puzzle_bank/spsa_datasets/le7_train.txt",
             "puzzle_bank/spsa_datasets/size8_train.txt",
             "puzzle_bank/spsa_datasets/size9_train.txt"))
        puzzles = calibration.read_puzzles(calibration.DEFAULT_DATASETS, 128)
        self.assertEqual({n: sum(p["size"] == n for p in puzzles)
                          for n in (7, 8, 9)}, {7: 128, 8: 128, 9: 128})
        self.assertEqual(len({p["identity"] for p in puzzles}), 384)
        self.assertTrue(all(p["dataset"].startswith(
            "puzzle_bank/spsa_datasets/") for p in puzzles))
        self.assertEqual(puzzles, calibration.read_puzzles(
            calibration.DEFAULT_DATASETS, 128))
        self.assertNotEqual(
            [p["identity"] for p in puzzles],
            [p["identity"] for p in calibration.read_puzzles(
                calibration.DEFAULT_DATASETS, 128, seed=73)])
        self.assertEqual(calibration.puzzle_mode({"size": 7}, None), 0)
        self.assertEqual(calibration.puzzle_mode({"size": 8}, None), 1)
        self.assertEqual(calibration.puzzle_mode({"size": 9}, None), 1)

    def test_seeded_spsa_perturbations(self):
        puzzles = [{"size": n} for n in (7, 8, 9)]
        configs = calibration.variants(puzzles, True, seed=1234)
        self.assertEqual(len(configs), 37)
        self.assertEqual(configs, calibration.variants(puzzles, True, seed=1234))
        self.assertNotEqual(configs, calibration.variants(puzzles, True, seed=4321))
        for n, group in ((7, "le7"), (8, "s8"), (9, "s9")):
            selected = [c for c in configs
                        if calibration.applicable(c, {"size": n})]
            self.assertEqual(len(selected), 13)
            for pair in range(6):
                left, right = selected[1 + 2 * pair:3 + 2 * pair]
                self.assertEqual(set(left["parameters"]),
                                 set(calibration.PARAMETER_GROUPS[group]))
                for name in left["parameters"]:
                    self.assertAlmostEqual(
                        left["parameters"][name] + right["parameters"][name], 2.0)
                    self.assertGreater(left["parameters"][name], 0.0)
                    self.assertGreater(right["parameters"][name], 0.0)

    def test_millisecond_optimizer_retains_second_unit_outputs(self):
        samples = [{"counters": {"setup_cell": i},
                    "runtime_median_seconds": 0.00025 + 0.00001 * i}
                   for i in range(10)]
        fit = calibration.fit_nonnegative(samples, ("setup_cell",))
        self.assertEqual(fit["optimizer_target_unit"], "milliseconds")
        self.assertAlmostEqual(fit["intercept_seconds"], 0.00025, places=8)
        self.assertAlmostEqual(
            fit["seconds_per_count"]["setup_cell"], 0.00001, places=8)

    def test_merge_exact_collinear_features(self):
        from work_collinearity import analyze_and_merge
        rows = []
        for idx in range(16):
            counts = {name: 0 for name in calibration.COUNTER_NAMES}
            counts["cache_pair_copy"] = 3 * idx + 2
            counts["cache_state_copy"] = 2 * counts["cache_pair_copy"]
            counts["base_score"] = idx * idx
            rows.append({"counters": counts,
                         "runtime_median_seconds": idx + 1})
        analysis = analyze_and_merge(rows, calibration.COUNTER_NAMES)
        groups = [g["members"] for g in analysis["groups"]]
        self.assertTrue(any(
            set(["cache_pair_copy", "cache_state_copy"]).issubset(set(g))
            for g in groups))
        self.assertEqual(analysis["rank_after"]["effective_rank"], 2)
        self.assertIn("setup_cell", analysis["constant_counters"])

    def test_four_fits_and_puzzle_stratification(self):
        rows = []
        for n in (7, 8, 9):
            for i in range(8):
                for config, amount in (("baseline", 1), ("variant", 2)):
                    counts = {name: 0 for name in calibration.COUNTER_NAMES}
                    counts["base_score"] = n * i + amount
                    counts["cache_pair_copy"] = i * i + amount
                    rows.append({
                        "size": n, "dataset": str(n), "line": i,
                        "identity": str(n) + ":" + str(i),
                        "configuration": config, "counters": counts,
                        "runtime_median_seconds":
                            0.05 + 0.001 * counts["base_score"]
                            + 0.0001 * counts["cache_pair_copy"],
                    })
        train, validation = calibration.split(rows, 0.25, 72)
        for n in (7, 8, 9):
            self.assertEqual(sum(r["size"] == n for r in train), 12)
            self.assertEqual(sum(r["size"] == n for r in validation), 4)
        fits, comparisons = calibration.fit_four_models(
            train, validation, 0.995, 1e-3)
        self.assertEqual(set(fits), {"size7", "size8", "size9", "all"})
        self.assertTrue(all(f["status"] == "fitted" for f in fits.values()))
        self.assertEqual(set(comparisons), {"size7", "size8", "size9"})
        self.assertEqual(fits["all"]["validation"]["samples"], 12)

    def test_metric_ranking_uses_same_puzzle(self):
        coefficients = {"intercept_seconds": 0.0,
                        "seconds_per_count": {"setup_cell": 0.5}}
        rows = [{"dataset": "one", "line": 1, "configuration": config,
                 "runtime_median_seconds": runtime, "size": 7,
                 "counters": {"setup_cell": count}}
                for config, runtime, count in
                [("baseline", 1.0, 2), ("variant", 2.0, 4)]]
        metrics = calibration.diagnostics(rows, coefficients)
        self.assertEqual(metrics["ranking_pairs"], 1)
        self.assertEqual(metrics["ranking_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
