"""Regression coverage for SPSA provenance, cohorts and paired validation.

Run: python3 -m unittest discover -s python_scripts/tests -v
"""
import argparse
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import types
import unittest
from unittest.mock import patch, Mock

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import analyze_spsa_runs as analysis
import compare_performance as comparison
from comparison_measurements import measure_batch
from spsa_metrics import get_sgm_shifts, shifted_geo_mean
from spsa_run_metadata import build_run_metadata, clue_identity, save_run_metadata
import spsa_tune as tuning


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / 'scratch')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def winner(self, name, values, metadata=None):
        path = self.directory / name
        path.write_text('SPSA WINNING PARAMETERS FOR SIZE 8 (Final SWA; mode=math)\n' +
                        ''.join(f'#define {key} {value}\n' for key, value in values.items()))
        if metadata is not None:
            path.with_suffix('.json').write_text(json.dumps(metadata))
        return str(path)

    def test_training_and_validation_use_identical_shifts_for_every_mode(self):
        datasets = {f's{size}_train': ['clue'] for size in (7, 8, 9)}
        for size in (7, 8, 9):
            for enumeration_only in (False, True):
                with self.subTest(size=size, enumeration_only=enumeration_only):
                    with patch.object(tuning, 'get_env_for_theta', return_value={}), \
                         patch.object(tuning, 'get_random_symmetry', side_effect=lambda clue: clue), \
                         patch.object(tuning, 'evaluate_subset', return_value=([0.1, 0.5], [100, 900])):
                        evaluator = tuning.build_loss_evaluator(size, datasets, 2, 1, True, enumeration_only)
                        _, _, observed = evaluator([])
                    single = get_sgm_shifts(size, enumeration_only)
                    enum = get_sgm_shifts(size, True)
                    expected = (shifted_geo_mean([0.1, 0.5], single[0]),
                                shifted_geo_mean([100, 900], single[1]),
                                shifted_geo_mean([0.1, 0.5], enum[0]),
                                shifted_geo_mean([100, 900], enum[1]))
                    if size == 9:
                        expected = expected[:2]
                    for actual, target in zip(observed, expected):
                        self.assertAlmostEqual(actual, target)
                    rows = [{'seconds': 0.1, 'nodes': 100}, {'seconds': 0.5, 'nodes': 900}]
                    summary = comparison.summarize(rows, single)
                    self.assertAlmostEqual(summary['sgm_time'], expected[0])
                    self.assertAlmostEqual(summary['sgm_nodes'], expected[1])

    def test_signal_thresholds_ignore_percent_shift_and_small_absolute_spread(self):
        strong = analysis.parameter_statistics([0.0494, 0.0495, 0.0496], 0.05)
        self.assertEqual(strong['signal'], 'STRONG SIGNAL')
        self.assertLess(abs(strong['shift_pct']), 2)
        noisy = analysis.parameter_statistics([0.1, 0.99, 2.0], 1.0)
        self.assertEqual(noisy['signal'], 'FLAT / NOISE')
        tiny = analysis.parameter_statistics([1e-8, 2e-8, 3e-8], 1e-7)
        self.assertGreater(tiny['s_ratio'], 2)
        self.assertEqual(analysis.parameter_statistics([4.0], 1.0)['signal'], 'INSUFFICIENT RUNS')

    def test_cohorts_preserve_historical_baselines_and_missing_sample_counts(self):
        key, other = 'WEIGHT_TOTAL_SCALE_S8', 'LOOKAHEAD_ENTROPY_WEIGHT_S8'
        metadata = {'size': 8, 'tune_mode': 'math', 'defaults': {key: 100, other: 0.05},
                    'active_parameters': [key, other], 'complete': True, 'seed': 1}
        one = self.winner('one.txt', {key: 110, other: 0.04}, metadata)
        two = self.winner('two.txt', {key: 112}, dict(metadata, seed=2))
        reports = analysis.analyze_files([one, two])
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]['parameters'][key]['baseline'], 100)
        self.assertEqual(reports[0]['parameters'][key]['n'], 2)
        self.assertEqual(reports[0]['parameters'][other]['n'], 1)
        three = self.winner('three.txt', {key: 113}, dict(metadata, defaults={key: 110}))
        four = self.winner('four.txt', {key: 114}, dict(metadata, tune_mode='strategy'))
        five = self.winner('five.txt', {key: 115}, dict(metadata, datasets={'train': {'sha256': 'different'}}))
        self.assertEqual(len(analysis.analyze_files([one, two, three, four, five])), 4)

    def test_provenance_round_trip_contains_seed_revision_defaults_and_dataset(self):
        args = argparse.Namespace(size=8, tune_mode='math', seed=42, log=None, batch_size=None)
        parameters = [('X', 0, 10, 2, int, 0.5)]
        metadata = build_run_metadata(args, {'train': ['a', 'b']}, parameters, {'X'}, 2, {'X': 2})
        self.assertEqual(metadata['seed'], 42)
        self.assertEqual(metadata['defaults'], {'X': 2})
        self.assertEqual(metadata['datasets']['train'], clue_identity(['a', 'b']))
        self.assertNotEqual(clue_identity(['a', 'b']), clue_identity(['b', 'a']))
        self.assertIn('python_scripts/spsa_tune.py', metadata['source_sha256'])
        self.assertTrue(metadata['revision'])
        path = self.directory / 'winner.txt'
        save_run_metadata(path, metadata, 'Started')
        self.assertFalse(json.loads(path.with_suffix('.json').read_text())['complete'])
        save_run_metadata(path, metadata, 'Final SWA')
        self.assertTrue(json.loads(path.with_suffix('.json').read_text())['complete'])
        self.assertFalse(list(self.directory.glob('*.tmp')))

    def test_seed_controls_optimizer_randomness(self):
        observed = []
        args = argparse.Namespace(seed=42, max_workers=1, log=None, size=8,
                                  iterations=1, no_compare=True)
        with patch.object(tuning, 'parse_args', return_value=args), \
             patch.object(tuning, 'load_datasets', return_value={}), \
             patch.object(tuning, 'run_spsa', side_effect=lambda *args: observed.append(random.random())), \
             redirect_stdout(io.StringIO()):
            tuning.main()
            tuning.main()
        self.assertEqual(observed[0], observed[1])

    def test_optimizer_saves_analyzable_winner_with_original_defaults(self):
        args = argparse.Namespace(size=8, tune_mode='math', seed=42, log=None,
                                  batch_size=2, iterations=1, alpha=0.0, gamma=0.0,
                                  perturb=0.03, lr=0.0001, beta=0.9,
                                  grad_clip=2.5, mom_clip=1.5, stdin=True,
                                  enumeration_only=False)
        path = self.directory / 'integrated.txt'
        with patch.object(tuning, 'resolve_winners_filename', return_value=str(path)), \
             patch.object(tuning, 'build_loss_evaluator', return_value=lambda theta: (1, 1, (0.1, 100, 0.2, 200))), \
             patch.object(tuning, 'RUN_METADATA', None), redirect_stdout(io.StringIO()):
            tuning.run_spsa(args, {'s8_train': ['clue'], 's8_val': ['other']}, 1)
        sidecar = json.loads(path.with_suffix('.json').read_text())
        self.assertTrue(sidecar['complete'])
        self.assertEqual(sidecar['seed'], 42)
        self.assertEqual(sidecar['sgm_shifts']['enumeration'], {'time': 2.0, 'nodes': 100000.0})
        size, mode, _ = analysis.parse_run_file(path)
        self.assertEqual((size, mode), (8, 'math'))
        report = analysis.analyze_files([str(path)])[0]
        self.assertEqual(len(report['parameters']), 13)
        self.assertEqual(report['baseline_source'], 'run metadata')

    def test_balanced_order_fixed_workers_and_persistent_records(self):
        def fake_batch(binary, options, clues, env, **kwargs):
            return [{'index': i, 'clue': clue, 'seconds': 1 if binary == 'baseline' else 0.9,
                     'nodes': 100, 'solutions': 1, 'status': 'ok'} for i, clue in enumerate(clues)]
        records = self.directory / 'instances.jsonl'
        with patch.object(comparison, 'measure_batch', side_effect=fake_batch) as measured, \
             redirect_stdout(io.StringIO()):
            reports = comparison.run_comparison(
                [('dataset', '-s 1', ['a', 'b'])], 'baseline', 'optimized',
                size=9, max_workers=2, repeats=2, records_path=str(records))
        self.assertEqual([call.args[0] for call in measured.call_args_list],
                         ['baseline', 'optimized', 'optimized', 'baseline'])
        self.assertTrue(all(call.kwargs['workers'] == 2 for call in measured.call_args_list))
        self.assertTrue(reports[0]['valid'])
        self.assertAlmostEqual(reports[0]['summary']['total_time']['diff_pct'], -10)
        self.assertEqual(reports[0]['sgm_shifts'], (1.0, 120000.0))
        self.assertEqual(len(records.read_text().splitlines()), 8)
        self.assertTrue((self.directory / 'instances_summary.json').exists())

    def test_comparison_infers_compact_and_delimited_clue_sizes(self):
        for clue in ('1' * 28, ' '.join(['1'] * 32), ','.join(['1'] * 36)):
            with self.subTest(clue=clue):
                row = {'index': 0, 'clue': clue, 'seconds': 1, 'nodes': 100,
                       'solutions': None, 'status': 'ok'}
                with patch.object(comparison, 'measure_batch', return_value=[row]):
                    report = comparison.evaluate_set(
                        [clue], '-s 1', 'dataset', 'base', 'opt', log_print=lambda *args: None)
                self.assertIn(report['size'], (7, 8, 9))
                self.assertEqual(report['sgm_shifts'], get_sgm_shifts(report['size']))

    def test_failures_and_solution_mismatches_invalidate_comparison(self):
        for status, solutions in [('timeout', 1), ('error', 1), ('ok', 2)]:
            with self.subTest(status=status, solutions=solutions):
                def fake_batch(binary, *args, **kwargs):
                    return [{'index': 0, 'clue': 'a', 'seconds': 1, 'nodes': 100,
                             'solutions': solutions if binary == 'optimized' else 1,
                             'status': status if binary == 'optimized' else 'ok'}]
                with patch.object(comparison, 'measure_batch', side_effect=fake_batch):
                    report = comparison.evaluate_set(
                        ['a'], '-s 1', 'dataset', 'baseline', 'optimized',
                        size=8, log_print=lambda *args: None)
                self.assertFalse(report['valid'])
                self.assertNotIn('summary', report)

    def fake_solver(self):
        script = self.directory / 'solver'
        script.write_text('''#!/usr/bin/env python3
import sys, time

def solve(clue, stdin):
    if 'timeout' in clue:
        time.sleep(1)
    if 'bad' not in clue:
        print('Nodes visited: 123')
        print('Solutions found: 1')
    if stdin:
        print('--- END_OF_INSTANCE ---')
    sys.stdout.flush()

if '--stdin' in sys.argv:
    for line in sys.stdin:
        solve(line, True)
else:
    solve(sys.argv[-1], False)
''')
        script.chmod(0o755)
        return str(script)

    def test_subprocess_modes_retain_failures_and_restart_stdin_workers(self):
        binary = self.fake_solver()
        for stdin in (True, False):
            with self.subTest(stdin=stdin):
                rows = measure_batch(binary, '-s 1', ['ok', 'bad', 'ok', 'timeout', 'ok'],
                                     None, workers=1, use_stdin=stdin, warmup=0, timeout=0.2)
                self.assertEqual([row['status'] for row in rows], ['ok', 'error', 'ok', 'timeout', 'ok'])
                self.assertEqual([row['index'] for row in rows], list(range(5)))
                self.assertIsNone(rows[3]['nodes'])
                self.assertEqual(rows[-1]['nodes'], 123)

    def test_baseline_environment_removes_inherited_tuning_overrides(self):
        key = 'WEIGHT_TOTAL_SCALE_S8'
        with patch.dict('os.environ', {key: '999', 'CUSTOM_SPSA_TEST': 'preserve'}):
            env = comparison.default_environment()
        self.assertNotIn(key, env)
        self.assertEqual(env['CUSTOM_SPSA_TEST'], 'preserve')

    def test_fetch_preserves_multiple_winners_and_metadata_without_collisions(self):
        api = Mock()
        kaggle = types.ModuleType('kaggle')
        kaggle.api = api
        requests = types.ModuleType('requests')
        requests.RequestException = type('RequestException', (Exception,), {})
        spec = importlib.util.spec_from_file_location('fetch_test', SCRIPTS / 'fetch_kaggle_runs.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'kaggle': kaggle, 'requests': requests}):
            spec.loader.exec_module(module)
        files = [types.SimpleNamespace(file_name=f'scratch/winners_s8_{i}.{ext}', url=f'{i}-{ext}')
                 for i in range(2) for ext in ('txt', 'json')]
        destination = str(self.directory / 'run_{index}.txt')
        with patch.object(module, 'get_latest_version_number', return_value=10), \
             patch.object(module, 'list_version_output_files', return_value=files), \
             patch.object(module, 'download_file') as downloaded, \
             patch.object(sys, 'argv', ['fetch', '--versions', '10', '--dest', destination]), \
             redirect_stdout(io.StringIO()):
            module.main()
        paths = [call.args[1] for call in downloaded.call_args_list]
        self.assertEqual(len(paths), 4)
        self.assertEqual(len(set(paths)), 4)
        self.assertEqual(sum(path.endswith('.json') for path in paths), 2)


if __name__ == '__main__':
    unittest.main()
