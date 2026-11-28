"""Strict work-tuning parser, objective, time + nodes opt-in, and runner smoke tests."""
import json
import subprocess
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
from spsa_run_metadata import build_run_metadata, save_run_metadata
from param_metadata import PARAM_METADATA


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

    def test_bundled_default_calibration_is_ready_for_tuning(self):
        model, sha = load_model(DEFAULT_MODEL)
        self.assertTrue(model["usable_for_tuning"])
        self.assertEqual(model["status"], "complete")
        self.assertFalse(model.get("provisional_allocation", False))
        self.assertFalse(model.get("unresolved_groups"))
        self.assertEqual(DEFAULT_MODEL.parent.name, "calibration")
        self.assertEqual(model["fit"], "pooled")
        self.assertEqual(len(model["seconds_per_count"]), 48)
        self.assertEqual(len(sha), 64)
        self.assertTrue(all(v is not None for v in
                            model["seconds_per_count"].values()))

    def test_spsa_startup_metadata_accepts_path_work_model(self):
        # Reproduce the default --work-model Path from argparse. Previously
        # json.dumps() raised TypeError before the first SPSA iteration.
        argv = ["spsa_tune.py", "--size", "9", "--iterations", "400",
                "--batch-size", "256", "--seed", "13959159128998499823"]
        with patch.object(sys, "argv", argv):
            args = spsa_tune.parse_args()
        self.assertIsInstance(args.work_model, Path)
        metadata = build_run_metadata(
            args, {"train": ["a"], "validation": ["b"]},
            PARAM_METADATA, set(), 4, {})
        self.assertEqual(metadata["config"]["work_model"], str(DEFAULT_MODEL))
        metadata["nested_paths"] = {
            "extra": [Path("scratch") / "calibration.json"]}
        with tempfile.TemporaryDirectory() as directory:
            winners = Path(directory) / "spsa_winners_s9_0.txt"
            save_run_metadata(winners, metadata, "Started")
            saved = json.loads(winners.with_suffix(".json").read_text())
            self.assertEqual(saved["config"]["work_model"],
                             str(DEFAULT_MODEL))
            self.assertEqual(saved["nested_paths"]["extra"],
                             ["scratch/calibration.json"])
            self.assertEqual(saved["label"], "Started")
            self.assertFalse(saved["complete"])
            save_run_metadata(winners, metadata, "Final")
            self.assertTrue(json.loads(
                winners.with_suffix(".json").read_text())["complete"])

    def test_unavailable_fresh_calibration_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                load_model(Path(directory) / "nonexistent.json")

    def test_incomplete_saved_model_is_rejected_for_tuning(self):
        model, _ = self._fixture_model()
        model["status"] = "incomplete"
        model["usable_for_tuning"] = False
        model["seconds_per_count"]["assignment"] = None
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "partial.model.json"
            target.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unresolved work calibration"):
                load_model(target)

    def test_provisional_model_is_usable_with_warning(self):
        model, _ = self._fixture_model()
        model.update(status="provisional", usable_for_tuning=True,
                     provisional_allocation=True, unresolved_groups=["example"])
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "provisional.model.json"
            target.write_text(json.dumps(model), encoding="utf-8")
            with self.assertWarnsRegex(RuntimeWarning, "Provisional work calibration"):
                loaded, _ = load_model(target)
            self.assertTrue(loaded["usable_for_tuning"])

    def test_incomplete_search_counter_record_is_rejected(self):
        model, _ = self._fixture_model()
        for status in ("timeout", "invalid"):
            with self.assertRaisesRegex(ValueError, "search"):
                parse_record([example_record(model), f"SEARCH_STATUS {status}"], model)
        self.assertEqual(parse_record([example_record(model), "SEARCH_STATUS complete"], model)[1], 7)

    def test_search_timeout_penalized_and_environment_sanitized(self):
        model, _ = self._fixture_model()
        proc = MagicMock()
        output = [example_record(model), "Nodes visited: 7",
                  "SEARCH_STATUS timeout", "--- END_OF_INSTANCE ---"]
        proc.communicate.return_value = ("\n".join(output), "")
        proc.returncode = 0
        env = {"SOLVER_CPU_TIMEOUT": "1", "SOLVER_MAIN_NODE_LIMIT": "1", "KEEP": "yes"}
        for selected in (None, model):
            with self.subTest(work=selected is not None), \
                 patch.object(spsa_tune, "WORK_MODEL", selected), \
                 patch.object(spsa_tune, "WORK_WATCHDOG_SECONDS", 2), \
                 patch.object(spsa_tune, "read_with_timeout", return_value=output), \
                 patch.object(spsa_tune.subprocess, "Popen", return_value=proc) as popen:
                self.assertEqual(spsa_tune.run_solver_instance(env, "-s 1", "clue"),
                                 (40.0, 100000))
                self.assertEqual(spsa_tune._run_opt_group_stdin(env, "-s 1", [(0, "clue")]),
                                 [(0, 40.0, 100000)])
                for call in popen.call_args_list:
                    self.assertEqual(call.kwargs["env"], {"KEEP": "yes"})
        self.assertIn("SOLVER_CPU_TIMEOUT", env)

    def test_unvalidated_complete_model_warns_but_remains_usable(self):
        model, _ = self._fixture_model()
        model.update(status="complete", usable_for_tuning=True,
                     allocated_validation_status="not_evaluated")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "candidate.model.json"
            target.write_text(json.dumps(model), encoding="utf-8")
            with self.assertWarnsRegex(RuntimeWarning, "not been evaluated"):
                loaded, _ = load_model(target)
            self.assertTrue(loaded["usable_for_tuning"])

    def test_work_watchdog_aborts_without_scoring(self):
        model, _ = self._fixture_model()
        proc = MagicMock()
        proc.communicate.side_effect = [subprocess.TimeoutExpired("solver", 2), ("", "")]
        with patch.object(spsa_tune, "WORK_MODEL", model), \
             patch.object(spsa_tune, "WORK_WATCHDOG_SECONDS", 2), \
             patch.object(spsa_tune.subprocess, "Popen", return_value=proc):
            with self.assertRaisesRegex(RuntimeError, "no wall-clock penalty"):
                spsa_tune.run_solver_instance({}, "-s 1", "clue")
            proc.kill.assert_called()
            proc.communicate.assert_any_call(timeout=2)
        with patch.object(spsa_tune, "WORK_MODEL", model), \
             patch.object(spsa_tune, "WORK_WATCHDOG_SECONDS", 2), \
             patch.object(spsa_tune, "read_with_timeout", return_value=None) as read, \
             patch.object(spsa_tune.subprocess, "Popen", return_value=proc):
            with self.assertRaisesRegex(RuntimeError, "no wall-clock penalty"):
                spsa_tune._run_opt_group_stdin({}, "-s 1", [(0, "clue")])
            read.assert_called_once_with(proc, timeout=2)

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
