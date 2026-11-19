"""Coordinate search, objective weights, frozen parameters and CLI integration."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python_scripts'))
import sweep_tune as sweep
from param_metadata import EFFECTIVE_DEPTH_PARAM_NAMES, get_active_param_names
from spsa_metrics import get_sgm_shifts, mean_log_shifted


class SweepTests(unittest.TestCase):
    def test_group_membership_and_default_panel_sizes(self):
        for size in (7, 8, 9):
            names = set(sweep.active_parameters(f'math{size}'))
            self.assertEqual(len(names), 22)
            suffix = '_LE7' if size == 7 else f'_S{size}'
            self.assertTrue(all(n.endswith(suffix) for n in names))
            self.assertEqual(names, get_active_param_names('math', size))
            self.assertTrue(EFFECTIVE_DEPTH_PARAM_NAMES <= get_active_param_names('strategy', size))
            self.assertEqual(get_active_param_names('all', size),
                             names | get_active_param_names('strategy', size))
        self.assertEqual(set(sweep.active_parameters('effective-depth')), EFFECTIVE_DEPTH_PARAM_NAMES)
        self.assertTrue(EFFECTIVE_DEPTH_PARAM_NAMES <= set(sweep.active_parameters('strategy')))
        args = sweep.parse_args(['--mode', 'math9'])
        self.assertEqual((args.s7_single, args.s7_enumeration), (2048, 512))
        self.assertEqual((args.s8_single, args.s8_enumeration, args.s9_single), (1024, 64, 2084))
        self.assertEqual(sweep.mode_sizes('math7'), [7])
        for mode in ('strategy', 'effective-depth'):
            self.assertEqual(sweep.mode_sizes(mode), [8, 9])
            self.assertFalse(any(n.endswith('_LE7') for n in sweep.active_parameters(mode)))
        self.assertEqual(sweep.affected_sizes('NUM_SET_WARP_0_LE7', [7, 8, 9]), [7])

    def test_fixed_panels_are_seeded_and_sample_without_replacement(self):
        clues = [' '.join([str(i)] * 32) for i in range(6)]
        data = dict(s8_train=clues)
        counts = {(8, False): 4, (8, True): 2}
        a = sweep.sample_panels(data, [8], counts, random.Random(42))
        b = sweep.sample_panels(data, [8], counts, random.Random(42))
        self.assertEqual(a, b)
        for panel in a.values():
            self.assertEqual(len(panel['indices']), len(set(panel['indices'])))
        with self.assertRaisesRegex(ValueError, 'need 7'):
            sweep.sample_panels(data, [8], {(8, False): 7}, random.Random(1))

    def test_objective_preserves_mode_means_not_sample_count_weights(self):
        values = sweep.default_values()
        panels = dict(single=dict(size=8, enumeration=False, clues=['a'] * 4),
                      enum=dict(size=8, enumeration=True, clues=['b']),
                      nine=dict(size=9, enumeration=False, clues=['c'] * 2))
        def evaluate(env, tasks, max_workers, use_stdin):
            if tasks[0][0] == '-s 0':
                return [3.] * len(tasks), [300000] * len(tasks)
            return [0.3] * len(tasks), [30000] * len(tasks)
        with patch.object(sweep.spsa, 'evaluate_subset', side_effect=evaluate):
            results = sweep.PanelObjective(panels, 4, True)(values, [8, 9])
        t8 = .5 * mean_log_shifted([.3], .2, .1) + 1.5 * mean_log_shifted([3.], 2., 1.)
        n8 = .5 * mean_log_shifted([30000], 10000, 5000) + 1.5 * mean_log_shifted([300000], 100000, 50000)
        self.assertAlmostEqual(results[8]['time'], t8)
        self.assertAlmostEqual(results[8]['nodes'], n8)
        self.assertAlmostEqual(results[8]['score'], .64 * t8 + .36 * n8)
        t9, n9 = get_sgm_shifts(9)
        expected9 = .66 * mean_log_shifted([.3], t9, .1) + .34 * mean_log_shifted([30000], n9, 20000)
        self.assertAlmostEqual(results[9]['score'], expected9)
        self.assertAlmostEqual(sweep.combined_score(results), (results[8]['score'] + expected9) / 2)

    def test_candidates_enforce_pair_constraints_and_deduplicate_integers(self):
        values = sweep.default_values()
        low = 'PRUNE_MIN_ENTROPY_CONSTR_PROP_LINE_P25'
        high = 'CONSTR_LOCAL_MAX_ENTROPY_P25'
        for name in (low, high):
            for value in sweep.candidate_values(name, values, 50):
                candidate = dict(values, **{name: value})
                self.assertLessEqual(candidate[low], candidate[high] + .05)
                self.assertEqual(candidate[high if name == low else low], values[high if name == low else low])
        grid = sweep.candidate_values('PRUNE_MIN_ENTROPY_GLOBAL_P25', values, 1e-12)
        self.assertEqual(len(grid), 1)
        self.assertEqual(len(next(iter(grid.values()))), 9)

    def test_finer_grid_covers_half_width_probes_and_total_scales_allow_1500(self):
        values = sweep.default_values()
        name = 'GLOBAL_ENTROPY_MULTIPLIER_S8'
        _, low, high, _, _, scale = sweep.PARAMETERS[name]
        values[name] = (low + high) / 2
        width = (high - low) * scale * .03
        offsets = sorted((v - values[name]) / width
                         for v in sweep.candidate_values(name, values, .03))
        expected = [-4, -2, -1, -.5, 0, .5, 1, 2, 4]
        self.assertEqual(len(offsets), len(expected))
        for actual, target in zip(offsets, expected):
            self.assertAlmostEqual(actual, target)
        for suffix in ('LE7', 'S8', 'S9'):
            name = f'WEIGHT_TOTAL_SCALE_{suffix}'
            self.assertEqual(sweep.PARAMETERS[name][1], 1500)
            values[name] = 1600
            grid = sweep.candidate_values(name, values, .03)
            self.assertEqual(min(grid), 1500)

    def test_le7_panels_preserve_mixed_sizes_and_match_size8_mode_weights(self):
        clues = [' '.join(['1'] * (4 * size)) for size in (5, 6, 7)]
        panels = sweep.sample_panels({'s7_train': clues}, [7],
                    {(7, False): 3, (7, True): 2}, random.Random(42))
        self.assertEqual(set(panels), {'s7_single', 's7_enumeration'})
        self.assertEqual(sorted(len(c.split()) for c in panels['s7_single']['clues']), [20, 24, 28])
        def evaluate(env, tasks, max_workers, use_stdin):
            t, n = (.04, 6000) if tasks[0][0] == '-s 0' else (.01, 500)
            return [t] * len(tasks), [n] * len(tasks)
        with patch.object(sweep.spsa, 'evaluate_subset', side_effect=evaluate):
            result = sweep.PanelObjective(panels, 1, True)(sweep.default_values(), [7])[7]
        self.assertEqual(sweep.MODE_WEIGHTS[7], sweep.MODE_WEIGHTS[8])
        time_loss = (.5 * mean_log_shifted([.01], .002, .005)
                     + 1.5 * mean_log_shifted([.04], .005, .01))
        node_loss = (.5 * mean_log_shifted([500], 100, 350)
                     + 1.5 * mean_log_shifted([6000], 1000, 2000))
        self.assertAlmostEqual(result['time'], time_loss)
        self.assertAlmostEqual(result['nodes'], node_loss)
        self.assertAlmostEqual(result['score'], .7 * time_loss + .3 * node_loss)

    def test_math7_main_loads_only_le7_and_dispatches_its_comparison(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'scratch') as folder:
            path = Path(folder) / 'le7_winner.txt'
            clues = [' '.join(['1'] * 20), ' '.join(['1'] * 28)]
            data = dict(s7_train=clues, s7_val=clues)
            for skip in (True, False):
                argv = ['--mode', 'math7', '--seed', '42', '--s7-single', '2', '--s7-enumeration', '1']
                if skip:
                    argv.append('--no-compare')
                with patch.object(sweep, 'output_path', return_value=path), \
                     patch.object(sweep, 'active_parameters', return_value=['GLOBAL_ENTROPY_MULTIPLIER_LE7']), \
                     patch.object(sweep.spsa, 'load_datasets', return_value=data) as load, \
                     patch.object(sweep.spsa, 'evaluate_subset', side_effect=lambda env, tasks, *a: ([.01] * len(tasks), [500] * len(tasks))), \
                     patch.object(sweep.spsa, 'run_post_tuning_comparison') as compare, redirect_stdout(io.StringIO()):
                    sweep.main(argv)
                load.assert_called_once_with(7)
                metadata = json.loads(path.with_suffix('.json').read_text())
                self.assertTrue(metadata['complete'])
                self.assertEqual(metadata['sizes'], [7])
                self.assertEqual(set(metadata['panels']), {'s7_single', 's7_enumeration'})
                self.assertEqual(set(metadata['datasets']), {'s7_train', 's7_val'})
                self.assertEqual(compare.call_count, 0 if skip else 1)
                if not skip:
                    self.assertEqual(compare.call_args.args[0].size, 7)

    def test_sequential_updates_cache_no_move_and_preserve_frozen_parameters(self):
        values = sweep.default_values()
        names = ['GLOBAL_ENTROPY_MULTIPLIER_S9', 'WEIGHT_TOTAL_SCALE_S9']
        targets = {}
        for name in names:
            _, low, high, _, _, scale = sweep.PARAMETERS[name]
            # Exercise all eight probes independently of tuned defaults near bounds.
            values[name] = (low + high) / 2
            targets[name] = values[name] + 2 * .03 * scale * (high - low)
        calls = []
        def objective(candidate, sizes):
            calls.append(dict(candidate))
            score = sum(((candidate[n] - targets[n]) / max(1, abs(targets[n]))) ** 2 for n in names)
            return {9: dict(score=score)}
        final, results, history = sweep.coordinate_sweep(values, names, [9], objective,
                    random.Random(3), .03, log=lambda *_: None)
        self.assertEqual(len(calls), 1 + 8 * len(names))
        for name in names:
            self.assertAlmostEqual(final[name], targets[name])
        self.assertTrue(all(final[n] == v for n, v in values.items() if n not in names))
        self.assertLess(results[9]['score'], 1e-20)
        second = history[1]
        earlier = history[0]
        self.assertTrue(all(call[earlier['parameter']] == earlier['selected'] for call in calls[9:]))
        self.assertTrue(second['trials'][0]['cached'])

    def test_candidate_evaluates_only_affected_size_and_ties_keep_start(self):
        values = sweep.default_values()
        calls = []
        def objective(candidate, sizes):
            calls.append(sizes)
            return {s: dict(score=float(s)) for s in sizes}
        final, _, _ = sweep.coordinate_sweep(values, ['GLOBAL_ENTROPY_MULTIPLIER_S8'],
                [8, 9], objective, random.Random(1), .03, log=lambda *_: None)
        self.assertEqual(calls[0], [8, 9])
        self.assertTrue(all(s == [8] for s in calls[1:]))
        self.assertEqual(final, values)

    def test_main_exports_sparse_complete_winner_and_comparison_dispatch(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'scratch') as folder:
            path = Path(folder) / 'winner.txt'
            clue = ' '.join(['1'] * 32)
            data = {f's{s}_{split}': [clue] * 2 for s in (8, 9) for split in ('train', 'val')}
            for skip in (True, False):
                argv = ['--mode', 'strategy', '--seed', '3', '--s8-single', '1',
                        '--s8-enumeration', '1', '--s9-single', '1']
                if skip:
                    argv.append('--no-compare')
                name = 'EFFECTIVE_DEPTH_C0'
                with patch.object(sweep, 'output_path', return_value=path), \
                     patch.object(sweep, 'active_parameters', return_value=[name]), \
                     patch.object(sweep.spsa, 'load_datasets', return_value=data), \
                     patch.object(sweep.spsa, 'evaluate_subset', side_effect=lambda env, tasks, *a: ([.1] * len(tasks), [100] * len(tasks))), \
                     patch.object(sweep.spsa, 'run_post_tuning_comparison') as compare, redirect_stdout(io.StringIO()):
                    sweep.main(argv)
                metadata = json.loads(path.with_suffix('.json').read_text())
                self.assertTrue(metadata['complete'])
                self.assertEqual(metadata['comparison_status'], 'skipped' if skip else 'complete')
                self.assertEqual(metadata['active_parameters'], [name])
                self.assertEqual(len(metadata['history']), 1)
                self.assertEqual(metadata['parameter_order'], [name])
                self.assertEqual([line.split()[1] for line in path.read_text().splitlines() if line.startswith('#define')], [name])
                self.assertEqual(compare.call_count, 0 if skip else 2)
                if not skip:
                    self.assertEqual([c.args[0].size for c in compare.call_args_list], [8, 9])
                    self.assertNotEqual(compare.call_args_list[0].args[0].log, compare.call_args_list[1].args[0].log)

    def test_wrapper_dispatch_help_and_misplaced_sweep_do_not_compile(self):
        result = subprocess.run(['bash', 'setup_and_tune.sh', '--sweep', '--help'], cwd=ROOT,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('math8', result.stdout)
        self.assertNotIn('Compiling', result.stdout)
        result = subprocess.run(['bash', 'setup_and_tune.sh', '--size', '8', '--sweep'], cwd=ROOT,
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Compiling', result.stdout)


if __name__ == '__main__':
    unittest.main()
