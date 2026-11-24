"""Tests for independent post-calibration micro timing and split checks."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from work_micro_probe import run_verification, verify_splits


class IndependentMicroVerificationTests(unittest.TestCase):
    def test_timing_diagnostics_distinguish_missing_unstable_insufficient(self):
        from work_micro_constraints import controlled_member_costs
        bench = {"rounds": 3, "raw_measurements": [
            {"kind": "individual", "counter": "unstable", "round": i,
             "units": 1000, "cpu_seconds": v}
            for i, v in enumerate((.001, .001, .01))
        ] + [{"kind": "individual", "counter": "insufficient",
               "round": 0, "units": 1000, "cpu_seconds": .001}]}
        costs, details = controlled_member_costs(
            bench, expected_names=("missing", "unstable", "insufficient"))
        self.assertFalse(costs)
        self.assertEqual(details["missing"]["reason"], "not_benchmarked")
        self.assertEqual(details["unstable"]["reason"], "unstable")
        self.assertEqual(details["insufficient"]["reason"],
                         "insufficient_timing_evidence")

    def test_lookahead_dependency_is_resolved_when_benchmarked(self):
        from work_micro_constraints import allocate_merged_coefficients
        group = "index_copy_call+index_copy_pair+lookahead_scan"
        model = {"collinearity": {"groups": [{
            "name": group, "members": group.split("+"),
            "aggregation": "sum_raw_counts"}]},
            "seconds_per_count": {group: 1e-8}}
        rows = [{"counters": {name: 8 for name in group.split("+")}}]
        benchmark = {"rounds": 3, "raw_measurements": [
            {"kind": "individual", "counter": name, "round": rd,
             "units": 1000, "cpu_seconds": cost}
            for rd in range(3)
            for name, cost in (("index_copy_call", .002),
                               ("index_copy_pair", .001),
                               ("lookahead_scan", .004))]}
        result = allocate_merged_coefficients(model, rows, benchmark,
                                               {"sections": {}})
        self.assertTrue(result["all_merged_groups_resolved"])
        self.assertGreater(result["seconds_per_count"]["lookahead_scan"], 0)

    def test_equal_weight_merged_split_is_checked_not_assumed(self):
        summary = {"sections": {
            "index_copy_call": {
                "volume_counter": "index_copy_pair",
                "timed_affine_fit": {
                    "identifiable": True,
                    "seconds_per_volume_relative_to_call": 1.2,
                },
            },
            "line_score": {
                "volume_counter": "line_score_value",
                "timed_affine_fit": {
                    "identifiable": False,
                },
            },
        }}
        model = {"seconds_per_count": {
            "index_copy_call": 0.000001, "index_copy_pair": 0.000001,
            "line_score": 0.0, "line_score_value": 0.0,
        }}
        collinearity = {"merged_groups": [{
            "name": "index_copy_call+index_copy_pair",
            "members": ["index_copy_call", "index_copy_pair"],
        }]}
        result = verify_splits(summary, collinearity, model)
        self.assertEqual(result["consistent_splits"], 1)
        self.assertEqual(result["unresolved_splits"], 1)
        self.assertTrue(result["splits"]["index_copy_call"]["merged_together"])
        summary["sections"]["index_copy_call"]["timed_affine_fit"][
            "seconds_per_volume_relative_to_call"] = 4.0
        result = verify_splits(summary, collinearity, model)
        self.assertEqual(result["disagreeing_splits"], 1)
        self.assertEqual(result["splits"]["index_copy_call"][
            "ratio_disagreement_factor"], 4.0)

    def test_zero_weight_never_counts_as_success(self):
        summary = {"sections": {
            "index_copy_call": {
                "volume_counter": "index_copy_pair",
                "timed_affine_fit": {
                    "identifiable": True,
                    "seconds_per_volume_relative_to_call": 1.5,
                },
            },
        }}
        results = verify_splits(summary, {"merged_groups": []},
                                {"seconds_per_count": {
                                    "index_copy_call": 0.0,
                                    "index_copy_pair": 0.0,
                                }})
        self.assertEqual(results["checked_splits"], 0)
        self.assertEqual(results["unresolved_splits"], 1)

    def test_exact_postfit_allocation_and_no_refit(self):
        from work_micro_constraints import allocate_merged_coefficients
        model = {"seconds_per_count": {"a+b": 10.0},
                 "collinearity": {"groups": [{"name": "a+b",
                     "members": ["a", "b"], "aggregation": "sum_raw_counts"}]}}
        rows = [{"counters": {"a": 2 * i, "b": i}} for i in range(1, 8)]
        benchmark = {"rounds": 3, "raw_measurements": [
            {"kind": "individual", "counter": name, "round": rnd,
             "units": 10000, "cpu_seconds": 10000 * cost}
            for rnd in range(3)
            for name, cost in (("a", 1e-6), ("b", 3e-6))]}
        result = allocate_merged_coefficients(
            model, rows, benchmark, {"sections": {}})
        self.assertAlmostEqual(result["seconds_per_count"]["a"], 6.0)
        self.assertAlmostEqual(result["seconds_per_count"]["b"], 18.0)
        self.assertLess(result["groups"][0][
            "max_abs_training_prediction_drift_seconds"], 1e-12)
        self.assertEqual(model["seconds_per_count"]["a+b"], 10.0)

    def test_both_timing_sources_contribute_to_split(self):
        from work_micro_constraints import allocate_merged_coefficients
        model = {"seconds_per_count": {"index_copy_call+index_copy_pair": 1.0},
                 "collinearity": {"groups": [{
                     "name": "index_copy_call+index_copy_pair",
                     "members": ["index_copy_call", "index_copy_pair"],
                     "aggregation": "sum_raw_counts"}]}}
        rows = [{"counters": {"index_copy_call": 10, "index_copy_pair": 80}}]
        benchmark = {"rounds": 3, "raw_measurements": [
            {"kind": "individual", "counter": name, "round": rnd,
             "units": 10000, "cpu_seconds": cost}
            for rnd in range(3) for name, cost in (
                ("index_copy_call", 0.01), ("index_copy_pair", 0.03))]}
        section = {"sections": {"index_copy_call": {
            "observations": 20, "timed_affine_fit": {
                "identifiable": True,
                "seconds_per_volume_relative_to_call": 9.0}}}}
        allocated = allocate_merged_coefficients(
            model, rows, benchmark, section)
        coeff = allocated["seconds_per_count"]
        ratio = coeff["index_copy_pair"] / coeff["index_copy_call"]
        self.assertGreater(ratio, 3.0)
        self.assertLess(ratio, 9.0)
        sources = {e["source"] for e in allocated["groups"][0]["timing_evidence"]}
        self.assertEqual(sources, {"controlled_micro", "solver_section"})

    def test_missing_timing_never_defaults_to_equal_weights(self):
        from work_micro_constraints import allocate_merged_coefficients
        model = {"seconds_per_count": {"a+b": 1.0},
                 "collinearity": {"groups": [{
                     "name": "a+b", "members": ["a", "b"],
                     "aggregation": "sum_raw_counts"}]}}
        rows = [{"counters": {"a": 1, "b": 1}}]
        bench = {"rounds": 3, "raw_measurements": [
            {"kind": "individual", "counter": "a", "round": i,
             "units": 1000, "cpu_seconds": 0.002} for i in range(3)]}
        result = allocate_merged_coefficients(
            model, rows, bench, {"sections": {}})
        self.assertFalse(result["all_merged_groups_resolved"])
        self.assertEqual(result["seconds_per_count"], {"a": None, "b": None})
        self.assertEqual(result["groups"][0]["status"], "unresolved")
        self.assertEqual(result["unresolved_groups"][0][
            "missing_or_unstable_counters"], ["b"])
        self.assertIn("Controlled microbenchmark", result["warnings"][0])

    def test_unresolved_group_preserves_other_resolved_allocations(self):
        from work_micro_constraints import allocate_merged_coefficients
        groups = [
            {"name": name, "members": members, "aggregation": "sum_raw_counts"}
            for name, members in (("a+b", ["a", "b"]), ("c+d", ["c", "d"]))]
        model = {"seconds_per_count": {"a+b": 1.0, "c+d": 2.0},
                 "collinearity": {"groups": groups}}
        rows = [{"counters": {"a": 4, "b": 4, "c": 2, "d": 2}}]
        bench = {"rounds": 3, "raw_measurements": [
            {"kind": "individual", "counter": name, "round": i,
             "units": 1000, "cpu_seconds": cost}
            for i in range(3) for name, cost in
            (("a", .001), ("c", .001), ("d", .002))]}
        result = allocate_merged_coefficients(
            model, rows, bench, {"sections": {}})
        self.assertFalse(result["all_merged_groups_resolved"])
        self.assertIsNone(result["seconds_per_count"]["a"])
        self.assertIsNone(result["seconds_per_count"]["b"])
        self.assertGreater(result["seconds_per_count"]["c"], 0)
        self.assertGreater(result["seconds_per_count"]["d"], 0)
        self.assertEqual(result["groups"][1]["status"], "resolved")

    def test_unresolved_split_still_retains_timing_observations(self):
        summary = {"sections": {
            "index_copy_call": {
                "volume_counter": "index_copy_pair",
                "timed_affine_fit": {
                    "identifiable": True,
                    "seconds_per_volume_relative_to_call": 5.0,
                },
            },
        }}
        group = "index_copy_call+index_copy_pair"
        collinearity = {"merged_groups": [{
            "name": group, "members": ["index_copy_call", "index_copy_pair"]}]}
        model = {"seconds_per_count": {
            "index_copy_call": 0.01, "index_copy_pair": 0.01}}
        result = verify_splits(summary, collinearity, model,
                               unresolved_groups=[group])
        self.assertEqual(result["checked_splits"], 0)
        self.assertEqual(result["unresolved_splits"], 1)
        split = result["splits"]["index_copy_call"]
        self.assertEqual(split["timed_volume_per_call_cost_ratio"], 5.0)
        self.assertIsNone(split["modeled_volume_per_call_cost_ratio"])
        self.assertEqual(split["verdict"], "unresolved")

    def test_validation_runs_with_unresolved_allocation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            model_path = path / "model.json"
            col_path = path / "collinearity.json"
            output = path / "micro.json"
            model_path.write_text(json.dumps({
                "status": "incomplete", "usable_for_tuning": False}))
            col_path.write_text(json.dumps({
                "counter_schema": "v1", "merged_groups": []}))
            puzzle = {"size": 8, "identity": "puzzle-id",
                      "dataset": "size8_val.txt", "line": 1}
            diagnostic_model = {"fit": "pooled", "counter_schema": "v1",
                                "seconds_per_count": {"assignment": 0.5}}
            with patch("work_micro_probe.read_puzzles",
                       return_value=[puzzle]), \
                 patch("work_micro_probe.verify_model",
                       return_value={
                           "overall": {"sections": {}},
                           "split_verification": {"checked_splits": 0},
                       }) as verify:
                report = run_verification(
                    model_path, col_path, output,
                    puzzles_per_size=1, controlled_result={
                        "rounds": 0, "raw_measurements": [], "sections": {}},
                    diagnostic_model=diagnostic_model,
                    unresolved_groups=["assignment+constraint_check_call"])
            self.assertEqual(report["status"],
                             "completed_with_unresolved_allocation")
            self.assertEqual(report["validation_basis"],
                             "pooled_merged_regression_projection")
            self.assertEqual(json.loads(output.read_text())["status"],
                             "completed_with_unresolved_allocation")
            self.assertEqual(verify.call_count, 1)
            self.assertEqual(verify.call_args.kwargs["unresolved_groups"],
                             ("assignment+constraint_check_call",))

    def test_automatic_verification_writes_independent_report(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            model_path = folder / "model.json"
            col_path = folder / "col.json"
            target = folder / "micro.json"
            model_path.write_text(json.dumps({"counter_schema": "v1"}))
            col_path.write_text(json.dumps({"counter_schema": "v1"}))
            dataset = folder / "dataset.txt"
            # Use the existing SPSA dataset instead of an artificial puzzle.
            with patch("work_micro_probe.read_puzzles", return_value=[
                    {"size": 8, "identity": "puzzle-id",
                     "dataset": "size8_val.txt", "line": 1,
                     "clue": "dummy", "grid": None}]), \
                 patch("work_micro_probe.verify_model", return_value={
                     "overall": {"plausibility_score": 0.9},
                     "split_verification": {"checked_splits": 1},
                 }) as check, \
                 patch("work_micro_probe.controlled_microbench", return_value={
                     "sections": {},
                 }):
                result = run_verification(
                    model_path, col_path, target, puzzles_per_size=1)
            check.assert_called_once()
            self.assertEqual(result["puzzle_counts_by_size"]["8"], 1)
            self.assertEqual(json.loads(target.read_text())[
                "overall"]["plausibility_score"], 0.9)
            self.assertEqual(len(result["model_file_sha256"]), 64)
            self.assertEqual(result["controlled_split_verification"][
                "checked_splits"], 0)

    def test_controlled_benchmark_runs_real_operations(self):
        from work_micro_probe import controlled_microbench
        report = controlled_microbench(repeats=1000, rounds=1)
        self.assertEqual(set(report["sections"]), {
            "cache_pair_copy_call", "line_score", "index_copy_call",
            "constraint_check_call"})
        self.assertEqual(sum(r["kind"] == "individual" for r in report["raw_measurements"]), 33)
        assignment = [r for r in report["raw_measurements"]
                      if r.get("counter") == "assignment"]
        self.assertEqual(len(assignment), 1)
        self.assertEqual(assignment[0]["timing_scope"], "paired_residual")
        self.assertGreater(assignment[0]["gross_cpu_seconds"], 0)
        self.assertGreater(assignment[0]["nested_cpu_seconds"], 0)
        self.assertAlmostEqual(
            assignment[0]["gross_cpu_seconds"]
            - assignment[0]["nested_cpu_seconds"],
            assignment[0]["cpu_seconds"], delta=1e-9)
        self.assertEqual(assignment[0]["nested_invalidation_attempts_per_unit"], 18)
        self.assertEqual(assignment[0]["nested_dirty_enqueues_per_unit"], 2)
        self.assertEqual(sum(r["kind"] == "affine" for r in report["raw_measurements"]), 16)
        counters = {r.get("counter") for r in report["raw_measurements"]
                    if r["kind"] == "individual"}
        self.assertTrue({"lookahead_scan", "resume_scan", "rescore_scan",
                         "base_score", "rel_entropy_value", "node_copy",
                         "solution_copy"} <= counters)
        self.assertEqual(report["coverage"]["expected_counters"], 48)
        self.assertNotIn("lookahead_scan", report["coverage"]["not_benchmarked"])
        self.assertTrue(all(r["cpu_seconds"] > 0
                            for r in report["raw_measurements"]
                            if r.get("counter") != "assignment"))
        # The paired residual may be indistinguishable from zero or
        # negative due to noise; preserve the raw timing instead of failing.
        self.assertTrue(report["sections"]["cache_pair_copy_call"][
            "timed_affine_fit"]["identifiable"])


if __name__ == "__main__":
    unittest.main()
