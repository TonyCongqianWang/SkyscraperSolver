"""Winner files and reports contain only the parameters actually tuned."""
import argparse
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python_scripts'))
import spsa_tune as tuning


class ReportingTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=ROOT / 'scratch')
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)

    def test_sparse_winners_for_each_mode_and_size(self):
        theta = tuning.project_constraints(tuning.get_default_theta())
        physical = tuning.get_physical_params(theta)
        for size in (7, 8, 9):
            for mode in ('math', 'strategy', 'all'):
                with self.subTest(size=size, mode=mode):
                    active = tuning.get_active_param_names(mode, size)
                    path = self.folder / 'winner.txt'
                    with patch.object(tuning, 'RUN_METADATA', None):
                        tuning.save_winners(path, theta, 'Intermediate', size, active)
                    values = {line.split()[1]: line.split()[2]
                              for line in path.read_text().splitlines() if line.startswith('#define')}
                    self.assertEqual(set(values), active)
                    for name in active:
                        self.assertEqual(values[name], str(physical[name]))

    def test_optimizer_excludes_frozen_parameters_and_reports_final_swa_change(self):
        parameters = [('ACTIVE_FLOAT', 0, 10, 5, float, 1),
                      ('ACTIVE_INT', 0, 10, 5, int, 1),
                      ('FROZEN', 3, 3, 3, float, 1),
                      ('INACTIVE', 0, 10, 5, float, 1)]
        args = argparse.Namespace(size=8, tune_mode='math', seed=42, log=None,
                                  batch_size=2, iterations=3, alpha=0, gamma=0,
                                  perturb=.03, lr=.01, beta=.9, grad_clip=2.5,
                                  mom_clip=1.5, stdin=True, enumeration_only=False)
        metadata = dict(tune_mode='math')
        output = io.StringIO()
        path = self.folder / 'winner.txt'
        loss = lambda theta: (theta[0], theta[0], (.1, 100, .2, 200))
        with patch.object(tuning, 'PARAM_METADATA', parameters), \
             patch.object(tuning, 'project_constraints', side_effect=list), \
             patch.object(tuning, 'get_active_param_names', return_value={'ACTIVE_FLOAT', 'ACTIVE_INT', 'FROZEN'}), \
             patch.object(tuning, 'resolve_winners_filename', return_value=str(path)), \
             patch.object(tuning, 'build_run_metadata', return_value=metadata) as build, \
             patch.object(tuning, 'RUN_METADATA', None), \
             patch.object(tuning, 'build_loss_evaluator', return_value=loss), redirect_stdout(output):
            final = tuning.run_spsa(args, {'s8_train': ['clue'], 's8_val': ['other']}, 1)
            physical = tuning.get_physical_params(final)
        self.assertEqual(build.call_args.args[3], {'ACTIVE_FLOAT', 'ACTIVE_INT'})
        definitions = {line.split()[1] for line in path.read_text().splitlines() if line.startswith('#define')}
        self.assertEqual(definitions, {'ACTIVE_FLOAT', 'ACTIVE_INT'})
        text = output.getvalue()
        self.assertNotIn('FROZEN', text)
        self.assertNotIn('INACTIVE', text)
        self.assertIn('Start', text)
        self.assertIn('End', text)
        self.assertIn('Abs. Change', text)
        # The first table reports the actual physical SWA endpoint, including integer rounding.
        rows = [line.split('|') for line in text.splitlines() if line.startswith('ACTIVE_FLOAT')]
        self.assertAlmostEqual(float(rows[0][1]), 5)
        self.assertAlmostEqual(float(rows[0][2]), physical['ACTIVE_FLOAT'], places=8)
        self.assertAlmostEqual(float(rows[0][3]), abs(physical['ACTIVE_FLOAT'] - 5), places=8)
        self.assertAlmostEqual(float(rows[1][-1]), abs(physical['ACTIVE_FLOAT'] - 5), places=8)
        self.assertIn('N/A', rows[1][1])  # One direction still cannot estimate sensitivity.

    def test_absolute_change_is_unsigned_and_uses_physical_units(self):
        active = {'WEIGHT_TOTAL_SCALE_S8', 'SEL_POWER_CELL_S8'}
        initial = {'WEIGHT_TOTAL_SCALE_S8': 1400, 'SEL_POWER_CELL_S8': -.52}
        final = {'WEIGHT_TOTAL_SCALE_S8': 1350, 'SEL_POWER_CELL_S8': -.51}
        output = io.StringIO()
        count = len(tuning.PARAM_METADATA)
        with redirect_stdout(output):
            tuning.report_parameter_values(initial, final, active)
            tuning.report_sensitivity_analysis([2.] * count, [4.] * count, 2,
                                              directions=2, active_names=active,
                                              initial_values=initial, final_values=final)
        rows = [line for line in output.getvalue().splitlines() if line.startswith('WEIGHT_TOTAL_SCALE_S8')]
        self.assertEqual(float(rows[0].split('|')[-1]), 50)
        self.assertEqual(float(rows[1].split('|')[-1]), 50)
        self.assertNotIn('WEIGHT_TOTAL_SCALE_S9', output.getvalue())


if __name__ == '__main__':
    unittest.main()
