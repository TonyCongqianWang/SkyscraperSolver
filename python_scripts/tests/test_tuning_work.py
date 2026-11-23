"""Strict work-tuning parser, objective, time + nodes opt-in, and runner smoke tests."""
import json
import tempfile
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import spsa_tune
import sweep_tune
from tuning_objective import (WORK, TIME_NODES, DEFAULT_OBJECTIVE,
                              mode_losses, spsa_components, sweep_score)
from tuning_work_runtime import load_model, parse_record, DEFAULT_MODEL
from calibrate_work import COUNTER_NAMES, SCHEMA


def example_record(model):
    counters = {key: 0 for key in COUNTER_NAMES}
    counters["assignment"] = 4
    return (f"WORK_COUNTERS {SCHEMA} solutions=1 nodes=7 "
            + " ".join(f"{key}={value}" for key, value in counters.items()))


class WorkTuningTests(unittest.TestCase):
    def _fixture_model(self):
        fixture = {
            "format": "skyscraper-work-model",
            "format_version": 1,
            "fit": "pooled",
            "counter_schema": SCHEMA,
            "intercept_seconds": 0.002,
            "seconds_per_count": {name: 1e-9 for name in COUNTER_NAMES},
        }
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "work_calibration.model.json"
            file.write_text(json.dumps(fixture), encoding="utf-8")
            return load_model(file)

    def test_unavailable_fresh_calibration_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                load_model(Path(directory) / "nonexistent.json")

    def test_calibrated_model_loads_and_schema_is_exact(self):
        model, digest = self._fixture_model()
        self.assertEqual(model["fit"], "pooled")
        self.assertEqual(model["counter_schema"], "v1")
        self.assertEqual(len(digest), 64)
        predicted, nodes, solutions = parse_record(
            [example_record(model)], model)
        self.assertEqual((nodes, solutions), (7, 1))
        self.assertAlmostEqual(predicted, model["intercept_seconds"]
                               + 4 * model["seconds_per_count"]["assignment"])

    def test_fail_closed_on_missing_or_incompatible_work_records(self):
        model, _ = self._fixture_model()
        record = example_record(model)
        for invalid in ([], [record, record], [record.replace(SCHEMA, "v99")],
                        [record.replace("assignment=4", "")],
                        [record.replace("assignment=4", "assignment=-4")]):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    parse_record(invalid, model)

    def test_default_and_explicit_time_nodes_modes(self):
        self.assertEqual(DEFAULT_OBJECTIVE, WORK)
        self.assertEqual(sweep_tune.parse_args(["--mode", "math8"]).objective, WORK)
        self.assertEqual(
            sweep_tune.parse_args(["--mode", "math8", "--nodes-time"]).objective,
            TIME_NODES)
        self.assertEqual(spsa_components(.1, .8, WORK), (.1, .1))
        self.assertEqual(spsa_components(.1, .8, TIME_NODES), (.1, .8))

    def test_sweep_pooled_work_uses_same_mode_loss_as_spsa(self):
        panels = {
            "single": dict(size=8, enumeration=False, clues=["c"]),
            "enumeration": dict(size=8, enumeration=True, clues=["d"]),
        }
        with patch.object(sweep_tune.spsa, "evaluate_subset",
                          side_effect=[([.5], [100]), ([2.0], [5000])]):
            result = sweep_tune.PanelObjective(panels, 1, False, WORK)(
                sweep_tune.default_values(), [8])[8]
        expected = (.5 * mode_losses(8, False, [.5], [100])[0]
                    + 1.5 * mode_losses(8, True, [2.0], [5000])[0])
        self.assertAlmostEqual(result["score"], expected)
        self.assertAlmostEqual(result["time"], expected)
        self.assertAlmostEqual(sweep_score(8, 1.1, 3.0, WORK), 1.1)

    def test_spsa_standalone_uses_work_not_wall_clock(self):
        model, _ = self._fixture_model()
        proc = MagicMock()
        proc.communicate.return_value = (example_record(model) + "\n", "")
        proc.returncode = 0
        with patch.object(spsa_tune, "WORK_MODEL", model), \
             patch.object(spsa_tune.subprocess, "Popen", return_value=proc):
            seconds, nodes = spsa_tune.run_solver_instance({}, "-s 1", "clue")
        self.assertEqual(nodes, 7)
        self.assertAlmostEqual(seconds, model["intercept_seconds"]
                               + 4 * model["seconds_per_count"]["assignment"])

    def test_stdin_batch_uses_work_not_pipe_latency(self):
        model, _ = self._fixture_model()
        proc = MagicMock()
        proc.stdin = MagicMock()
        lines = [example_record(model) + "\n", "--- END_OF_INSTANCE ---\n"]
        with patch.object(spsa_tune, "WORK_MODEL", model), \
             patch.object(spsa_tune, "read_with_timeout", return_value=lines), \
             patch.object(spsa_tune.subprocess, "Popen", return_value=proc):
            result = spsa_tune._run_opt_group_stdin(
                {}, "-s 1", [(0, "clue")])
        self.assertEqual(result[0][0], 0)
        self.assertEqual(result[0][2], 7)
        self.assertAlmostEqual(result[0][1], model["intercept_seconds"]
                               + 4 * model["seconds_per_count"]["assignment"])

    def test_regular_comparison_binaries_stay_native(self):
        self.assertTrue(spsa_tune.BIN_NATIVE.endswith("skyscraper_solver"))


if __name__ == "__main__":
    unittest.main()
