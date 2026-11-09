"""Bounded evaluation, routing, migration, and SPSA integration checks."""
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python_scripts'))
from param_metadata import PARAM_METADATA, PARAMETER_MAPPING, PARAM_CONSTRAINTS, get_active_param_names


class EffectiveDepthTests(unittest.TestCase):
    def test_production_evaluation_and_routing(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'scratch') as directory:
            binary = Path(directory) / 'checks'
            sources = [
                'params_math', 'params_math_getters', 'params_math_getters_lookahead',
                'params_effective_depth', 'params_int', 'params_double',
                'params_depth_arrays', 'params_depth_cubic', 'params_depth_bounds',
                'params_depth_eval_int', 'params_depth_eval_double1',
                'params_depth_eval_double2', 'entropy', 'entropy_weights', 'math_log',
                'pruning_configs', 'lookahead_depth', 'prune_strat_cfg_setup',
                'prune_strat_routing', 'prune_strat_initial',
            ]
            subprocess.run(['gcc', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=undefined', '-fno-sanitize-recover=all',
                            '-I', str(ROOT / 'src'),
                            str(Path(__file__).with_name('effective_depth_checks.c')),
                            *[str(ROOT / 'src' / f'{s}.c') for s in sources],
                            '-o', str(binary)], check=True, text=True)
            result = subprocess.run([str(binary)], check=True, capture_output=True, text=True)
            self.assertIn('checks passed', result.stdout)

    def test_joint_tuning_and_export(self):
        from spsa_tune import get_default_theta, get_physical_params, get_env_for_theta
        spec = importlib.util.spec_from_file_location(
            'overrides', ROOT / 'python_scripts/examples/apply_env_overrides.py')
        overrides = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(overrides)
        generated = {env: (var, kind) for _, variables, _ in overrides.FILES_CONFIGS
                     for var, env, kind in variables}
        self.assertEqual(len(PARAM_METADATA), len({p[0] for p in PARAM_METADATA}))
        theta = get_default_theta()
        physical = get_physical_params(theta)
        env = get_env_for_theta(theta)
        model_names = {p[0] for p in PARAM_METADATA if p[0].startswith(
            ('DEPTH_WARP', 'NUM_SET_WARP', 'EFFECTIVE_DEPTH', 'GLOBAL_ENTROPY_MULTIPLIER'))}
        self.assertEqual(len(model_names), 27)
        for size, suffix in [(7, 'LE7'), (8, 'S8'), (9, 'S9')]:
            active = get_active_param_names('all', size)
            expected = {n for n in model_names if n.endswith(suffix) or n.startswith('EFFECTIVE_DEPTH')}
            self.assertTrue(expected <= active)
            self.assertIn('INITIAL_GAC_GLOBAL_MIN_ENTROPY', active)
        self.assertFalse(any('WARP' in name for row in PARAM_CONSTRAINTS for name in row[:2]))
        self.assertFalse(any('UNSET_BIAS' in name for name in PARAMETER_MAPPING))
        for name in model_names | {n for n in physical if 'GLOBAL_MIN_ENTROPY' in n}:
            filepath, var, kind = PARAMETER_MAPPING[name]
            self.assertEqual(generated[name], (var, kind))
            match = re.search(rf'\b{var}\s*=\s*([^;]+)', (ROOT / filepath).read_text())
            self.assertAlmostEqual(float(match[1]), physical[name])
            self.assertAlmostEqual(float(env[name]), physical[name])
        for name, low, high, default, kind, scale in PARAM_METADATA:
            if 'GLOBAL_MIN_ENTROPY' in name:
                self.assertGreater(high, 1000000)  # No permanent reachability cap.
            if name.startswith(('DEPTH_WARP', 'NUM_SET_WARP')):
                self.assertAlmostEqual(.03 * scale * (high - low), .0054)
            if name.startswith('EFFECTIVE_DEPTH'):
                self.assertLess(low, 0)
                self.assertGreater(high, 1)
                self.assertAlmostEqual(.03 * scale * (high - low), .012)


if __name__ == '__main__':
    unittest.main()
