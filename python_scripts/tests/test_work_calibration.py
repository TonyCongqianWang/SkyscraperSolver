"""Smoke tests for the work-calibration fit; no external dependencies."""
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import sys
from unittest.mock import patch

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
            self.assertEqual(len(calibration.COUNTER_NAMES), 48)
            counts = first[3]
            self.assertGreater(counts["constraint_check_call"], 0)
            self.assertGreaterEqual(
                counts["constraint_check_cell"],
                counts["constraint_check_call"])
            self.assertGreaterEqual(
                counts["domain_invalidation_attempt"],
                counts["domain_invalidation"])
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

    def test_checkpoint_compiled_parity(self):
        puzzles = calibration.read_puzzles(
            ["puzzle_bank/spsa_datasets/size8_train.txt"], 1)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            variant = {"name": "checkpoint", "parameters": {}}
            plain, _ = calibration.build(directory, variant, True, "gcc", [])
            timed, _ = calibration.build(directory, variant, True, "gcc",
                                         ["-DWORK_MICRO_TIMING"])
            native, _ = calibration.build(directory, variant, False, "gcc", [])
            env = calibration.checkpoint_environment(None, checkpoint=1)
            a = calibration.execute(plain, puzzles[0], 1, 30, env=env,
                                    return_status=True)
            b = calibration.execute(timed, puzzles[0], 1, 30, env=env,
                                    include_micro=True, return_status=True)
            n = calibration.execute(native, puzzles[0], 1, 30, env=env,
                                    return_status=True)
            self.assertEqual(a[1:4], b[1:4])
            self.assertEqual(a[-1], b[-1])
            self.assertEqual(a[-1], n[-1])
            self.assertEqual(a[1:3], n[1:3])
            leader = calibration.execute(
                timed, puzzles[0], 1, 30, include_micro=True,
                env=calibration.checkpoint_environment(None, cpu_limit=1e-9),
                return_status=True)
            if not leader[-1]["complete"]:
                replay = calibration.execute(
                    plain, puzzles[0], 1, 30,
                    env=calibration.checkpoint_environment(
                        None, checkpoint=leader[-1]["main_nodes"]),
                    return_status=True)
                self.assertEqual(leader[1:4], replay[1:4])
                self.assertEqual(leader[-1], replay[-1])

    def test_checkpoint_replay_uses_leader_limit(self):
        counts = dict.fromkeys(calibration.COUNTER_NAMES, 1)
        status = {"complete": False, "main_nodes": 5}
        calls = []
        def run(kind, repeat, binary, include_micro=False,
                cpu_limit=None, checkpoint=None):
            calls.append((kind, cpu_limit, checkpoint))
            result = (0.01, 0, 12, None if kind == "native" else counts)
            return result + (([],) if include_micro else ()) + (status,)
        _, _, _, _, result = calibration.measure_checkpoint_observation(
            run, "plain", "native", "timed", 1, 2, 5)
        self.assertEqual(result, status)
        self.assertEqual(calls, [("micro", 5, None), ("instrumented", None, 5),
                                 ("native", None, 5), ("native", None, 5)])

    def test_partial_rows_excluded_from_ranking(self):
        model = {"intercept_seconds": 0.0, "seconds_per_count": {"setup_cell": 1}}
        rows = [dict(size=9, dataset="x", line=1, configuration=str(i),
                     counters={"setup_cell": i}, runtime_median_seconds=i,
                     complete=i == 1) for i in (1, 2)]
        result = calibration.diagnostics(rows, model)
        self.assertEqual(result["partial_samples"], 1)
        self.assertEqual(result["ranking_pairs"], 0)

    def test_unresolved_assignment_saves_all_reports_and_still_validates(self):
        from work_micro_probe import run_verification
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            output = folder / "work_calibration.json"
            puzzles = [{
                "size": 8, "identity": f"p{i}", "dataset": "dummy.txt",
                "dataset_sha256": "abcdef", "line": i + 1,
                "clue": "fake", "grid": [],
            } for i in range(2)]
            counts = dict.fromkeys(calibration.COUNTER_NAMES, 1)
            fit = {
                "intercept_seconds": 0.01,
                "seconds_per_count": {
                    "assignment+constraint_check_call": 0.0001},
                "ridge_alpha": 0.0, "contrast_weight": 0.0,
                "collinearity": {
                    "groups": [{
                        "name": "assignment+constraint_check_call",
                        "members": ["assignment", "constraint_check_call"],
                        "aggregation": "sum_raw_counts",
                    }],
                    "correlation_threshold": 0.995,
                    "dependency_tolerance": 1e-3,
                    "method": "test", "merge_events": [],
                    "correlated_pairs": [], "constant_counters": [],
                    "constant_merged_groups": [], "rank_before": {},
                    "rank_after": {}, "cost_assumption": "provisional",
                },
            }
            fits = {"all": {
                "status": "fitted", "coefficients": fit,
                "validation": {"samples": 1, "mae_seconds": 0.01}}}
            controlled = {"rounds": 3, "sections": {}, "raw_measurements": [
                {"kind": "individual", "counter": "constraint_check_call",
                 "round": i, "units": 1000, "cpu_seconds": 0.001}
                for i in range(3)]}

            def fake_execute(binary, puzzle, mode, timeout,
                             include_micro=False, env=None, return_status=False):
                result = (0.01, 1, 3,
                          counts if str(binary) == "instrumented" else None)
                return result + ({"complete": True, "main_nodes": 2},) if return_status else result

            def fake_verify(model_path, collinearity_path, micro_path, **kwargs):
                self.assertEqual(kwargs["unresolved_groups"],
                                 ["assignment+constraint_check_call"])
                self.assertTrue(kwargs["diagnostic_model"]["diagnostic_projection"])
                self.assertEqual(kwargs["diagnostic_model"][
                    "seconds_per_count"]["assignment"], 0.0001)
                report = {
                    "status": "completed_with_unresolved_allocation",
                    "split_verification": {"unresolved_splits": 1},
                }
                Path(micro_path).write_text(json.dumps(report))
                return report

            argv = ["calibrate_work.py", "--dataset", "dummy.txt",
                    "--puzzles-per-size", "2", "--native-repeats", "2",
                    "--no-perturb",
                    "--no-section-timing", "--micro-repeats", "1000",
                    "--micro-rounds", "3", "--seed", "1234",
                    "--output", str(output)]
            with patch.object(sys, "argv", argv), \
                 patch.object(calibration, "read_puzzles", return_value=puzzles), \
                 patch.object(calibration, "variants", return_value=[
                     {"name": "baseline", "parameters": {}}]), \
                 patch.object(calibration, "applicable", return_value=True), \
                 patch.object(calibration, "build",
                              side_effect=lambda *args: (
                                  Path("instrumented" if args[2] else "native"), [])), \
                 patch.object(calibration, "execute", side_effect=fake_execute), \
                 patch.object(calibration, "split",
                              side_effect=lambda rows, *args: (rows[:1], rows[1:])), \
                 patch.object(calibration, "fit_four_models",
                              return_value=(fits, {})), \
                 patch.object(calibration, "predict", return_value=0.01), \
                 patch.object(calibration, "diagnostics",
                              return_value={"samples": 1}), \
                 patch("work_micro_probe.controlled_microbench",
                       return_value=controlled), \
                 patch("work_micro_probe.run_verification",
                       side_effect=fake_verify) as verify:
                calibration.main()

            verify.assert_called_once()
            for path in (output, output.with_suffix(".raw.jsonl"),
                         output.with_suffix(".model.json"),
                         output.with_suffix(".collinearity.json"),
                         output.with_suffix(".micro.json")):
                self.assertTrue(path.exists(), str(path))
            detail = json.loads(output.read_text())
            self.assertEqual(detail["status"], "partial")
            self.assertEqual(detail["micro_verification_status"],
                             "completed_with_unresolved_allocation")
            self.assertEqual(len(detail["samples"]), 2)
            self.assertEqual(detail["provenance"]["instrumented_repeats"], 0.5)
            self.assertEqual(detail["provenance"]["effective_instrumented_repeats"], 1)
            self.assertTrue(all(row["counter_source"] == "instrumented"
                                for row in detail["samples"]))
            self.assertIsNone(detail["samples"][0]["predictions_seconds"][
                "pooled_allocated"])
            self.assertIn("assignment", detail["warnings"][0])
            model = json.loads(output.with_suffix(".model.json").read_text())
            self.assertFalse(model["usable_for_tuning"])
            self.assertIsNone(model["seconds_per_count"]["assignment"])
            self.assertEqual(len(output.with_suffix(".raw.jsonl").
                                 read_text().splitlines()), 6)

    def test_work_counter_names_describe_current_operations(self):
        from tuning_work_runtime import DEFAULT_MODEL
        actual = set(calibration.COUNTER_NAMES)
        self.assertIn("dp_candidate_check", actual)
        self.assertIn("cache_build_candidate", actual)
        self.assertIn("provisional_solution_rollback", actual)
        self.assertFalse({"gac_check", "cache_build_check", "rollback"} & actual)
        self.assertEqual(DEFAULT_MODEL.name, "work_calibration.model.json")
        self.assertEqual(len(actual), 48)

    def test_resume_reuses_partial_puzzle_and_rejects_incompatible_runs(self):
        puzzles = calibration.read_puzzles(
            ["puzzle_bank/spsa_datasets/size8_train.txt"], 1, seed=42)
        puzzle = puzzles[0]
        variant = {"name": "baseline", "parameters": {}}
        counts = {name: 0 for name in calibration.COUNTER_NAMES}
        event = {
            "configuration": variant["name"],
            "parameters": variant["parameters"],
            "dataset": puzzle["dataset"],
            "dataset_sha256": puzzle["dataset_sha256"],
            "line": puzzle["line"], "identity": puzzle["identity"],
            "size": puzzle["size"], "max_solutions": 1,
            "run_type": "instrumented", "instrumented": True,
            "run_index": 0, "elapsed_seconds": 0.002,
            "solutions": 1, "nodes": 4, "counters": counts,
        }
        with tempfile.TemporaryDirectory() as temp:
            journal = Path(temp) / "measurements.raw.jsonl"
            journal.write_text(json.dumps(event) + "\n", encoding="utf-8")
            found = calibration.load_completed_runs(
                journal, puzzles, [variant], None, 9, 3, True)
            key = calibration._raw_run_key("baseline", puzzle,
                                           "instrumented", 0)
            self.assertEqual(found[key], event)
            self.assertEqual(calibration._outcome_from_raw(event),
                             (0.002, 1, 4, counts))
            # A partial puzzle is valid. Exact duplicate invocations,
            # changed datasets and counter schemas are not.
            journal.write_text(json.dumps(event) + "\n" +
                               json.dumps(event) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                calibration.load_completed_runs(
                    journal, puzzles, [variant], None, 9, 3, True)
            changed = dict(event, dataset_sha256="incorrect")
            journal.write_text(json.dumps(changed) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mismatched"):
                calibration.load_completed_runs(
                    journal, puzzles, [variant], None, 9, 3, True)
            changed = dict(event, counters={"setup_cell": 1})
            journal.write_text(json.dumps(changed) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                calibration.load_completed_runs(
                    journal, puzzles, [variant], None, 9, 3, True)

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

    def test_default_workload_doubles_distinct_evaluations(self):
        sizes = {7: 6000, 8: 6000, 9: 6000}
        plan = calibration.calibration_workload_plan(
            sizes, perturb=True, native_repeats=2,
            instrumented_repeats=0.5, section_timing=True)
        self.assertEqual(plan["distinct_puzzles"], 18000)
        self.assertEqual(plan["configurations_per_puzzle"], 2)
        self.assertEqual(plan["puzzle_configuration_evaluations"], 36000)
        self.assertEqual(plan["native_solver_executions"], 72000)
        self.assertEqual(plan["instrumented_solver_executions"], 18000)
        self.assertEqual(plan["section_timing_solver_executions"], 18000)
        self.assertEqual(plan["total_solver_executions"], 108000)
        for rate, expected in ((0, 18000), (0.25, 18000), (1, 36000),
                               (1.5, 54000), (2, 72000)):
            plan = calibration.calibration_workload_plan(
                sizes, True, 2, rate, True)
            self.assertEqual(plan["instrumented_solver_executions"], expected)
            self.assertEqual(plan["section_timing_solver_executions"], 18000)
        for rate in (0, 0.5, 1):
            plan = calibration.calibration_workload_plan(
                {8: 2}, False, 2, rate, False)
            self.assertEqual(plan["total_solver_executions"], 6)
        for rate in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                calibration.calibration_workload_plan(sizes, True, 2, rate, True)

    def test_paired_section_schedule_is_seeded_and_order_independent(self):
        puzzles = [{"size": size, "identity": f"{size}-{i}",
                    "dataset": f"size{size}", "line": i}
                   for size in (7, 8, 9) for i in range(5)]
        configs = [{"name": p["identity"] + sign, "puzzle_identity": p["identity"]}
                   for p in puzzles for sign in ("_plus", "_minus")]
        sections = calibration.section_timing_schedule
        schedule = calibration.instrumented_repeat_schedule
        timed = sections(puzzles, configs, True, 42)
        self.assertEqual(len(timed), 15)
        self.assertEqual(timed, sections(
            list(reversed(puzzles)), list(reversed(configs)), True, 42))
        self.assertNotEqual(timed, sections(puzzles, configs, True, 43))
        for p in puzzles:
            self.assertEqual(sum(key[1:] == (p["dataset"], p["line"])
                                 for key in timed), 1)
        for rate, per_size in ((0, 5), (0.25, 5), (0.5, 5), (1, 10),
                               (1.5, 15), (2, 20)):
            chosen = schedule(puzzles, configs, rate, True, 42)
            self.assertEqual(chosen, schedule(
                list(reversed(puzzles)), list(reversed(configs)), rate, True, 42))
            for size in (7, 8, 9):
                self.assertEqual(sum(n for key, n in chosen.items()
                                     if key[1] == f"size{size}"), per_size)
            self.assertTrue(all(n or key in timed for key, n in chosen.items()))
            if rate <= 0.5:
                self.assertTrue(all(n == int(key not in timed)
                                    for key, n in chosen.items()))
        self.assertEqual(set(schedule(puzzles, configs, 0, False, 42).values()), {1})
        self.assertFalse(sections(puzzles, configs, False, 42))
        singles = configs[::2]
        self.assertEqual(len(sections(puzzles, singles, True, 42)), 9)
        self.assertEqual(sum(schedule(puzzles, singles, 0.5, True, 42).values()), 9)

    def test_section_timed_counters_authoritative_and_parity_optional(self):
        counts = dict.fromkeys(calibration.COUNTER_NAMES, 1)
        calls = []

        def run(kind, repeat, binary, include_micro=False):
            calls.append((kind, repeat))
            if kind == "micro":
                self.assertTrue(include_micro)
                return (9.0, 1, 3, counts, ["section"])
            if kind == "instrumented":
                return (7.0, 1, 3, dict(counts))
            return (0.01, 1, 3, None)

        for repeats in (0, 1, 2):
            calls.clear()
            first, times, plain, sections = calibration.measure_observation(
                run, "plain", "native", "timed", repeats, 2)
            self.assertIs(first[3], counts)
            self.assertEqual(first[0], 9.0)
            self.assertEqual(times, [0.01, 0.01])
            self.assertEqual(len(plain), repeats)
            self.assertEqual(sections, ["section"])
            self.assertEqual(calls, [("micro", 0)] +
                             [("instrumented", i) for i in range(repeats)] +
                             [("native", 0), ("native", 1)])
        first, times, plain, sections = calibration.measure_observation(
            run, "plain", "native", None, 1, 2)
        self.assertEqual(first[3], counts)
        self.assertEqual(len(plain), 1)
        self.assertEqual(sections, [])

        def mismatch(kind, repeat, binary, include_micro=False):
            if kind == "instrumented":
                return (7.0, 1, 3, dict(counts, assignment=2))
            return run(kind, repeat, binary, include_micro)

        with self.assertRaisesRegex(RuntimeError, "parity mismatch"):
            calibration.measure_observation(
                mismatch, "plain", "native", "timed", 1, 2)

        def missing(kind, repeat, binary, include_micro=False):
            return (9.0, 1, 3, None, [])

        with self.assertRaisesRegex(RuntimeError, "missing work counters"):
            calibration.measure_observation(
                missing, None, "native", "timed", 0, 2)

    def test_fractional_journal_rejects_unscheduled_runs_and_changed_plan(self):
        puzzles = [{"size": 8, "identity": f"p{i}", "dataset": "dummy.txt",
                    "dataset_sha256": "abc", "line": i} for i in range(4)]
        variants = [{"name": p["identity"], "puzzle_identity": p["identity"],
                     "parameters": {}} for p in puzzles]
        schedule = calibration.instrumented_repeat_schedule(
            puzzles, variants, 0.5, True, 42)
        run_plan = calibration.calibration_run_plan(42, 2, 0.5, True)
        counts = dict.fromkeys(calibration.COUNTER_NAMES, 0)

        def event(p, kind):
            value = {"configuration": p["identity"], "parameters": {},
                     "dataset": p["dataset"], "dataset_sha256": "abc",
                     "line": p["line"], "identity": p["identity"], "size": 8,
                     "max_solutions": 1, "run_type": kind, "run_index": 0,
                     "elapsed_seconds": 0.01, "solutions": 1, "nodes": 3,
                     "counters": counts, "run_plan": run_plan}
            if kind == "micro":
                value["micro_sections"] = []
            return value

        chosen = next(p for p in puzzles if schedule[
            (p["identity"], p["dataset"], p["line"])])
        skipped = next(p for p in puzzles if not schedule[
            (p["identity"], p["dataset"], p["line"])])
        with tempfile.TemporaryDirectory() as temp:
            journal = Path(temp) / "measurements.raw.jsonl"

            def write(*events):
                journal.write_text("".join(json.dumps(e) + "\n" for e in events))

            def load(rate=0.5, seed=42):
                return calibration.load_completed_runs(
                    journal, puzzles, variants, None, 2, rate, True, seed)

            write(event(chosen, "instrumented"), event(skipped, "micro"))
            self.assertEqual(len(load()), 2)
            with self.assertRaisesRegex(ValueError, "run plan"):
                load(rate=1)
            with self.assertRaisesRegex(ValueError, "run plan"):
                load(seed=43)
            write(event(skipped, "instrumented"))
            with self.assertRaisesRegex(ValueError, "mismatched"):
                load()
            write(event(chosen, "micro"))
            with self.assertRaisesRegex(ValueError, "mismatched"):
                load()
            old_plan = dict(run_plan, parity_sampling="seeded_size_stratified_hash_v1")
            write(dict(event(chosen, "instrumented"), run_plan=old_plan))
            with self.assertRaisesRegex(ValueError, "run plan"):
                load()

    def test_one_ellipsoid_pair_per_puzzle_perturbs_all_spsa_parameters(self):
        from param_metadata import PARAM_METADATA, get_active_param_names
        puzzles = [{"size": size, "identity": f"puzzle-{size}-{i}"}
                   for size in (7, 8, 9) for i in range(2)]
        configs = calibration.variants(puzzles, True, seed=1234)
        self.assertEqual(len(configs), len(puzzles) * 2)
        self.assertEqual(configs, calibration.variants(puzzles, True, seed=1234))
        self.assertNotEqual(configs, calibration.variants(puzzles, True, seed=4321))
        for i, puzzle in enumerate(puzzles):
            left, right = configs[2*i:2*i+2]
            self.assertEqual(left["puzzle_identity"], puzzle["identity"])
            self.assertEqual(right["puzzle_identity"], puzzle["identity"])
            active = get_active_param_names("all", puzzle["size"])
            self.assertEqual(set(left["parameters"]), active)
            self.assertEqual(set(right["parameters"]), active)
            self.assertNotEqual(left["parameters"], right["parameters"])
            for variant in (left, right):
                self.assertTrue(calibration.applicable(variant, puzzle))
                for name, low, high, *_ in PARAM_METADATA:
                    if name in active:
                        self.assertGreaterEqual(variant["parameters"][name], low)
                        self.assertLessEqual(variant["parameters"][name], high)
            self.assertFalse(calibration.applicable(
                left, puzzles[(i + 1) % len(puzzles)]))
        self.assertEqual(len(calibration.variants(puzzles, False, seed=1234)),
                         len(puzzles))

    def test_runtime_overlay_covers_every_spsa_parameter(self):
        from param_metadata import PARAM_METADATA, PARAMETER_MAPPING
        code = calibration.runtime_override_source()
        self.assertEqual(code.count(" = getenv("), len(PARAM_METADATA))
        for name, *_ in PARAM_METADATA:
            self.assertIn(f'getenv("{name}")', code)
            self.assertIn(PARAMETER_MAPPING[name][1], code)

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
