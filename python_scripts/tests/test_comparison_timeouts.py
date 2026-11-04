"""Timeouts are censored benchmark outcomes, not correctness failures."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python_scripts'))
import compare_performance as comparison
from comparison_statistics import pair_outcome, validate_policy
import spsa_tune as tuning


def row(index, status='ok', seconds=1, nodes=100, solutions=1):
    return dict(index=index, clue=str(index), status=status, seconds=seconds,
                nodes=nodes if status == 'ok' else None,
                solutions=solutions if status == 'ok' else None)


class TimeoutComparisonTests(unittest.TestCase):
    def evaluate(self, base, optimized):
        def batch(binary, *args, **kwargs):
            return base if binary == 'base' else optimized
        with patch.object(comparison, 'measure_batch', side_effect=batch), \
             redirect_stdout(io.StringIO()):
            return comparison.evaluate_set([str(i) for i in range(len(base))], '-s 1',
                                           'dataset', 'base', 'opt', size=8, timeout=10)

    def test_timeouts_penalized_and_never_dropped_from_time_metrics(self):
        report = self.evaluate([row(0, seconds=2), row(1, 'timeout'), row(2, 'timeout')],
                               [row(0, seconds=1), row(1, seconds=9), row(2, 'timeout')])
        self.assertTrue(report['valid'])
        self.assertEqual(report['summary']['total_time']['baseline'], 82)
        self.assertEqual(report['summary']['total_time']['optimized'], 50)
        self.assertEqual(report['summary']['total_nodes']['baseline'], 100)
        self.assertEqual(report['counts']['arms']['Baseline']['timeouts']['median'], 2)
        self.assertEqual(report['counts']['arms']['Optimized']['wins']['median'], 2)
        self.assertEqual(report['counts']['both_timeout']['median'], 1)
        self.assertEqual(report['counts']['paired_count']['median'], 1)
        self.assertEqual(report['rounds'][0]['instance_outcomes'][1]['winner'], 'Optimized')

    def test_all_timeouts_still_have_a_valid_time_summary_but_no_node_metrics(self):
        report = self.evaluate([row(0, 'timeout')], [row(0, 'timeout')])
        self.assertTrue(report['valid'])
        self.assertAlmostEqual(report['summary']['sgm_time']['baseline'], 40)
        self.assertIsNone(report['summary']['sgm_nodes']['baseline'])
        self.assertIsNone(report['summary']['total_nodes']['diff_pct'])
        self.assertEqual(report['counts']['arms']['Baseline']['wins']['median'], 0)
        self.assertEqual(report['counts']['arms']['Baseline']['near_best_wins']['median'], 0)

    def test_timing_tolerance_and_solved_vs_timeout_wins(self):
        self.assertEqual(pair_outcome(row(0, seconds=1), row(0, seconds=1.1), .1), 'tie')
        self.assertEqual(pair_outcome(row(0, seconds=1), row(0, seconds=1.11), .1), 'Baseline')
        self.assertEqual(pair_outcome(row(0, 'timeout', seconds=0), row(0, seconds=9), .1), 'Optimized')
        self.assertEqual(pair_outcome(row(0, seconds=9), row(0, 'timeout', seconds=0), .1), 'Baseline')
        report = self.evaluate([row(0, seconds=1)], [row(0, seconds=1.05)])
        for arm in ('Baseline', 'Optimized'):
            self.assertEqual(report['counts']['arms'][arm]['near_best_wins']['median'], 1)
            self.assertEqual(report['counts']['arms'][arm]['wins']['median'], 0)
        self.assertEqual(report['counts']['tie']['median'], 1)

    def test_errors_mismatches_and_misaligned_results_remain_invalid(self):
        for optimized in ([row(0, 'error')], [row(0, solutions=2)],
                          [row(1)], []):
            with self.subTest(optimized=optimized):
                report = self.evaluate([row(0)], optimized)
                self.assertFalse(report['valid'])
                self.assertNotIn('summary', report)

    def test_raw_timeout_records_and_scored_times_are_both_persisted(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'scratch') as temporary:
            path = Path(temporary) / 'records.jsonl'
            with patch.object(comparison, 'measure_batch', return_value=[row(0, 'timeout', seconds=11)]), \
                 redirect_stdout(io.StringIO()):
                reports = comparison.run_comparison([('dataset', '-s 1', ['0'])],
                                                   'base', 'opt', size=8, records_path=str(path))
            self.assertTrue(reports[0]['valid'])
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(r['status'] == 'timeout' and r['seconds'] == 11
                                and r['scored_seconds'] == 40 and r['timeout'] == 10 for r in rows))
            self.assertEqual(reports[0]['counts']['both_timeout']['median'], 1)

    def test_real_workers_restart_after_timeouts_in_both_subprocess_modes(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'scratch') as temporary:
            folder = Path(temporary)
            source = f"#!{sys.executable}\n" + '''import sys,time
from pathlib import Path

def solve(clue):
    clue = clue.strip().strip('"')
    slow = (Path(sys.argv[0]).name == 'base' and clue == '0') or (Path(sys.argv[0]).name == 'opt' and clue == '1')
    if slow:
        time.sleep(1)
    print('Nodes visited: 100')
    print('Solutions found: 1')
    if '--stdin' in sys.argv:
        print('--- END_OF_INSTANCE ---')
    sys.stdout.flush()

if '--stdin' in sys.argv:
    for line in sys.stdin:
        solve(line)
else:
    solve(sys.argv[-1])
'''
            for name in ('base', 'opt'):
                binary = folder / name
                binary.write_text(source)
                binary.chmod(0o755)
            for stdin in (False, True):
                with self.subTest(stdin=stdin), redirect_stdout(io.StringIO()):
                    reports = comparison.run_comparison(
                        [('tiny', '-s 1', ['0', '1', '2'])], str(folder / 'base'),
                        str(folder / 'opt'), size=8, timeout=.2, max_workers=1,
                        warmup=1, use_stdin=stdin, records_path=str(folder / f'{stdin}.jsonl'))
                report = reports[0]
                self.assertTrue(report['valid'])
                for arm in ('Baseline', 'Optimized'):
                    self.assertEqual(report['counts']['arms'][arm]['timeouts']['median'], 1)
                    self.assertEqual(report['counts']['arms'][arm]['errors']['median'], 0)
                    self.assertEqual(report['counts']['arms'][arm]['solved']['median'], 2)
                self.assertEqual(report['counts']['paired_count']['median'], 1)

    def test_policy_rejects_invalid_values(self):
        for policy in [(0, 2, .1), (float('nan'), 2, .1), (10, .5, .1),
                       (10, float('inf'), .1), (10, 2, -.1), (10, 2, float('nan'))]:
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                validate_policy(*policy)

    def test_post_tuning_forwards_comparison_policy_and_accepts_timeout_reports(self):
        args = type('Args', (), dict(size=9, enumeration_only=False, log=None,
                    stdin=True, seed=42, max_workers=2, comparison_repeats=2, comparison_warmup=0,
                    comparison_timeout=10, comparison_timeout_penalty=4,
                    comparison_win_tolerance=.1))()
        with patch.object(comparison, 'run_comparison', return_value=[{'valid': True}]) as run, \
             patch.object(tuning, 'get_env_for_theta', return_value={}):
            tuning.run_post_tuning_comparison(args, {'s9_train': ['a'], 's9_val': ['b']}, [])
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs['timeout'], 10)
            self.assertEqual(call.kwargs['timeout_penalty'], 4)
            self.assertEqual(call.kwargs['win_tolerance'], .1)


if __name__ == '__main__':
    unittest.main()
