"""Tests for section CPU timing parsers and calibration plausibility diagnostics."""
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calibrate_work as calibration
from work_section_plausibility import (
    TIMED_SECTIONS, expanded_coefficients, parse_micro_lines,
    summarize_plausibility,
)


class WorkSectionPlausibilityTests(unittest.TestCase):
    def _model(self):
        names = calibration.COUNTER_NAMES
        return {
            "seconds_per_count": {name: (
                2e-6 if name == "line_score"
                else 3e-7 if name == "line_score_value" else 0.0)
                for name in names},
            "collinearity": {"groups": [
                {"name": name, "members": [name],
                 "aggregation": "sum_raw_counts"}
                for name in names]},
        }

    def test_parse_v2_sampled_cpu_timing_and_volume(self):
        i = calibration.COUNTER_NAMES.index("line_score")
        source = [
            f"WORK_MICRO v2 counter={i} calls=128 samples=2 "
            "ticks=5000 clock_ticks_per_second=1000000000 sampled_volume=18"
        ]
        rows = parse_micro_lines(source, calibration.COUNTER_NAMES)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["samples"], 2)
        self.assertEqual(rows[0]["sampled_volume"], 18)
        self.assertAlmostEqual(rows[0]["sampled_cpu_seconds"], 5e-6)
        for bad in (source[0].replace("v2", "v1"),
                    source[0].replace("samples=2", "samples=200"),
                    source[0].replace("sampled_volume=18", ""),
                    source[0] + " extra=9"):
            with self.assertRaises(ValueError):
                parse_micro_lines([bad], calibration.COUNTER_NAMES)
        with self.assertRaises(ValueError):
            parse_micro_lines(source + source, calibration.COUNTER_NAMES)

    def test_plausibility_only_compares_matching_sampled_work(self):
        model = self._model()
        rows = []
        for samples, volume in [(1, 8), (3, 9), (5, 24), (9, 60)]:
            expected = 2e-6 * samples + 3e-7 * volume
            rows.append({"micro_sections": [{
                "section": "line_score",
                "samples": samples,
                "sampled_volume": volume,
                "sampled_cpu_seconds": expected * 1.4,
            }]})
        result = summarize_plausibility(rows, model, calibration.COUNTER_NAMES)
        self.assertAlmostEqual(result["plausibility_score"], 1.0)
        self.assertEqual(result["scored_sections"], 1)
        section = result["sections"]["line_score"]
        self.assertAlmostEqual(section["pearson_r"], 1.0)
        self.assertAlmostEqual(section["measured_to_model_ratio"], 1.4)
        self.assertEqual(section["total_sampled_packages"], 18)
        self.assertIsNone(result["sections"]["index_copy_call"]["pearson_r"])

    def test_timed_affine_cost_split_is_identifiable_across_sizes(self):
        from work_section_plausibility import timed_affine_fit
        samples = [
            (0.000002 * calls + 0.0000005 * volume, calls, volume)
            for calls, volume in ((20, 140), (80, 640), (100, 900),
                                  (15, 135), (5, 45), (100, 700))
        ]
        result = timed_affine_fit(samples)
        self.assertTrue(result["identifiable"])
        self.assertAlmostEqual(result["sampled_call_seconds"], 2e-6, places=11)
        self.assertAlmostEqual(result["sampled_volume_seconds"], 5e-7, places=11)
        self.assertAlmostEqual(
            result["seconds_per_volume_relative_to_call"], 0.25, places=6)
        ambiguous = timed_affine_fit(
            [(0.00001 * n, n, 8 * n) for n in (2, 3, 4, 5)])
        self.assertFalse(ambiguous["identifiable"])

    def test_zero_coefficients_and_timing_do_not_fake_correlation(self):
        model = self._model()
        model["seconds_per_count"]["line_score"] = 0.0
        model["seconds_per_count"]["line_score_value"] = 0.0
        rows = [
            {"micro_sections": [{
                "section": "line_score", "samples": i,
                "sampled_volume": 8 * i, "sampled_cpu_seconds": i * 0.1,
            }]} for i in (1, 2, 3)]
        result = summarize_plausibility(rows, model, calibration.COUNTER_NAMES)
        self.assertIsNone(result["plausibility_score"])
        self.assertIsNone(result["sections"]["line_score"]["pearson_r"])

    def test_optional_timing_binary_matches_counters(self):
        puzzles = calibration.read_puzzles(
            ["puzzle_bank/spsa_datasets/size8_train.txt"], 1)
        with tempfile.TemporaryDirectory() as directory:
            variant = {"name": "baseline", "parameters": {}}
            folder = Path(directory)
            instr, _ = calibration.build(folder, variant, True, "gcc", [])
            timed, _ = calibration.build(
                folder, variant, True, "gcc", ["-DWORK_MICRO_TIMING"])
            plain = calibration.execute(instr, puzzles[0], 1, 30)
            micro = calibration.execute(timed, puzzles[0], 1, 30,
                                        include_micro=True)
            self.assertEqual(plain[1:4], micro[1:4])
            for record in micro[4]:
                self.assertIn(record["section"], TIMED_SECTIONS)
                self.assertLessEqual(record["samples"], record["calls"])


if __name__ == "__main__":
    unittest.main()
