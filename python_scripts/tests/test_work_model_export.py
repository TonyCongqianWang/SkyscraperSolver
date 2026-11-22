"""Tests for a small executable pooled model, independent of a full run."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from work_model_export import export_compact_model, make_compact_model
from work_model_export import export_collinearity, make_collinearity_export
from work_model_export import load_compact_model, predict_seconds


def sample_report():
    return {
        "provenance": {
            "git_commit": "123abc", "schema": "v2",
            "counter_schema": [
                "node_copy", "cache_pair_copy_call", "cache_pair_copy",
                "line_score", "line_score_value", "unused",
            ],
            "datasets": [["train.txt", "abc"]],
            "compiler": "gcc fixture",
            "puzzles_per_size": {"7": 3, "8": 3, "9": 3},
            "max_solutions_by_size": {"7": 0, "8": 1, "9": 1},
        },
        "sample_counts": {"train": 9, "validation": 3},
        "fits": {
            "size7": {"status": "fitted",
                      "coefficients": {"intercept_seconds": 100.0}},
            "all": {
                "status": "fitted",
                "coefficients": {
                    "intercept_seconds": 0.2,
                    "seconds_per_count": {
                        "cache_pair_copy+cache_pair_copy_call": 0.01,
                        "line_score": 0.3,
                    },
                    "ridge_alpha": 0.0001, "contrast_weight": 4.0,
                    "collinearity": {
                        "correlation_threshold": 0.995,
                        "dependency_tolerance": 0.001,
                        "method": "centered_pairwise_pearson_then_pivoted_gram_schmidt",
                        "merge_events": [
                            {"type": "pairwise", "a": "cache_pair_copy",
                             "b": "cache_pair_copy_call", "pearson_r": 0.999}],
                        "correlated_pairs": [
                            {"a": "cache_pair_copy", "b": "cache_pair_copy_call",
                             "pearson_r": 0.999}],
                        "constant_counters": ["unused"],
                        "constant_merged_groups": [],
                        "rank_before": {"effective_rank": 2, "column_count": 3,
                                        "independent": [], "dependent": []},
                        "rank_after": {"effective_rank": 2, "column_count": 2,
                                       "independent": [], "dependent": []},
                        "cost_assumption": "equal per-unit cost within each merged group; provisional",
                        "groups": [
                        {"name": "cache_pair_copy+cache_pair_copy_call",
                         "members": ["cache_pair_copy", "cache_pair_copy_call"],
                         "aggregation": "sum_raw_counts"},
                        {"name": "line_score", "members": ["line_score"],
                         "aggregation": "sum_raw_counts"},
                    ]},
                },
                "validation": {
                    "samples": 3, "mae_seconds": 0.002, "r2": 0.98,
                    "clear_ranking_accuracy": 0.9,
                    "clear_ranking_coverage": 0.75,
                    "within_puzzle_r2": 0.85,
                },
            },
        },
        "pooled_validation_by_size": {
            "size7": {"mae_seconds": 0.002, "r2": 0.98,
                      "clear_ranking_accuracy": 0.9,
                      "clear_ranking_coverage": 0.5,
                      "within_puzzle_r2": 0.8},
        },
    }


class CompactExportTests(unittest.TestCase):
    def test_flattened_merged_model_exact_prediction(self):
        report = sample_report()
        model = make_compact_model(
            report, "calibration.json", "2026-11-22T12:00:00+00:00")
        self.assertEqual(model["fit"], "pooled")
        self.assertEqual(model["counter_schema"], "v2")
        self.assertEqual(model["created_at_utc"], "2026-11-22T12:00:00+00:00")
        self.assertEqual(model["dropped_counters"],
                         ["line_score_value", "node_copy", "unused"])
        counters = {
            "node_copy": 2, "cache_pair_copy_call": 3,
            "cache_pair_copy": 20, "line_score": 2,
            "line_score_value": 70, "unused": 17,
        }
        self.assertAlmostEqual(
            predict_seconds(model, counters),
            0.2 + 0.01 * (20 + 3) + 0.3 * 2)
        self.assertLess(len(json.dumps(model)), 3000)
        self.assertEqual(model["held_out_score"]["clear_ranking_accuracy"], 0.9)
        self.assertEqual(model["hyperparameters"]["contrast_weight"], 4.0)

    def test_pooled_collinearity_export_for_microbenchmarks(self):
        report = sample_report()
        timestamp = "2026-11-22T12:00:00+00:00"
        artifact = make_collinearity_export(report, "detailed.json", timestamp)
        self.assertEqual(artifact["fit"], "pooled")
        self.assertEqual(artifact["counter_schema"], "v2")
        self.assertEqual(artifact["created_at_utc"], timestamp)
        self.assertEqual(len(artifact["merged_groups"]), 1)
        self.assertEqual(artifact["merged_groups"][0]["members"],
                         ["cache_pair_copy", "cache_pair_copy_call"])
        self.assertEqual(artifact["merged_groups"][0][
            "seconds_per_merged_count"], 0.01)
        self.assertEqual(artifact["correlated_pairs"][0]["pearson_r"], 0.999)
        self.assertEqual(artifact["merge_events"][0]["type"], "pairwise")
        self.assertEqual(artifact["rank_before"]["effective_rank"], 2)
        self.assertEqual(artifact["constant_counters"], ["unused"])
        self.assertNotIn("size7", artifact)
        self.assertNotIn("samples", artifact)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "collinearity.json"
            export_collinearity(report, path, "detailed.json", timestamp)
            self.assertEqual(json.loads(path.read_text()), artifact)
            self.assertTrue(path.read_text().endswith("\\n"))

    def test_persist_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            export_compact_model(sample_report(), path,
                                 "detailed.json", "2026-11-22T12:00:00+00:00")
            model = load_compact_model(path)
            self.assertEqual(model["source_calibration_file"], "detailed.json")
            self.assertEqual(set(model["seconds_per_count"]),
                             set(sample_report()["provenance"]["counter_schema"]))

    def test_rejects_unknown_or_duplicate_group_members(self):
        report = sample_report()
        report["fits"]["all"]["coefficients"]["collinearity"]["groups"][0][
            "members"].append("unknown")
        with self.assertRaises(ValueError):
            make_compact_model(report)

    def test_runtime_rejects_mismatched_counter_schema(self):
        model = make_compact_model(sample_report())
        with self.assertRaises(ValueError):
            predict_seconds(model, {"node_copy": 1})


if __name__ == "__main__":
    unittest.main()
