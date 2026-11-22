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

    def test_automatic_verification_writes_independent_report(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            model_path = folder / "model.json"
            col_path = folder / "col.json"
            target = folder / "micro.json"
            model_path.write_text(json.dumps({"counter_schema": "v3"}))
            col_path.write_text(json.dumps({"counter_schema": "v3"}))
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
            "cache_pair_copy_call", "line_score", "index_copy_call"})
        self.assertEqual(len(report["raw_measurements"]), 13)
        self.assertTrue(all(r["cpu_seconds"] > 0
                            for r in report["raw_measurements"]))
        self.assertTrue(report["sections"]["cache_pair_copy_call"][
            "timed_affine_fit"]["identifiable"])


if __name__ == "__main__":
    unittest.main()
