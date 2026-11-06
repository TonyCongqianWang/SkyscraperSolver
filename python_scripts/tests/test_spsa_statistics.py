"""Exact sign probabilities, tie handling and family-wise correction."""
import math
import json
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from spsa_statistics import binomial_sign_test, holm_adjust, adjust_direction_tests
from analyze_spsa_runs import parameter_statistics, analyze_files


class SignTestTests(unittest.TestCase):
    def test_exact_two_sided_probabilities(self):
        self.assertEqual(binomial_sign_test(0, 0)['p_value'], 1)
        self.assertEqual(binomial_sign_test(3, 3)['p_value'], 1)
        self.assertEqual(binomial_sign_test(1, 0)['p_value'], 1)
        self.assertEqual(binomial_sign_test(0, 23)['p_value'], 2 ** -22)
        self.assertEqual(binomial_sign_test(30, 0)['p_value'], 2 ** -29)
        self.assertAlmostEqual(binomial_sign_test(29, 1)['p_value'], 62 / 2 ** 30)
        self.assertAlmostEqual(binomial_sign_test(18, 5)['p_value'],
                               2 * sum(math.comb(23, k) for k in range(6)) / 2 ** 23)
        self.assertEqual(binomial_sign_test(18, 5)['p_value'], binomial_sign_test(5, 18)['p_value'])

    def test_ties_do_not_inflate_trial_count(self):
        stats = parameter_statistics([1, 1, 2, 2, 2, 2], 1)
        self.assertEqual(stats['ties'], 2)
        self.assertEqual(stats['sign_test']['non_tied_runs'], 4)
        self.assertEqual(stats['sign_test']['agreement'], 1)
        self.assertEqual(stats['sign_test']['p_value'], .125)
        self.assertIsNone(parameter_statistics([1, 1], 1)['sign_test']['direction'])

    def test_holm_known_values_in_original_order(self):
        actual = holm_adjust([.04, .001, .03, .02])
        for got, expected in zip(actual, [.06, .004, .06, .06]):
            self.assertAlmostEqual(got, expected)
        self.assertEqual(holm_adjust([]), [])
        self.assertEqual(holm_adjust([1, 1]), [1, 1])

    def test_significance_uses_entire_supplied_family(self):
        rows = [parameter_statistics([2] * 7, 1), parameter_statistics([2] * 6 + [0], 1)]
        adjust_direction_tests(rows)
        self.assertTrue(rows[0]['sign_test']['significant'])
        self.assertFalse(rows[1]['sign_test']['significant'])
        self.assertEqual(rows[0]['sign_test']['family_tests'], 2)
        # A nominally significant 18/23 direction fails after testing 26 parameters.
        rows = [parameter_statistics([2] * 18 + [0] * 5, 1)]
        rows += [parameter_statistics([0, 2], 1) for _ in range(25)]
        adjust_direction_tests(rows)
        self.assertLess(rows[0]['sign_test']['p_value'], .05)
        self.assertGreater(rows[0]['sign_test']['p_holm'], .05)

    def test_required_agreement_depends_on_sample_count(self):
        for n, minimum in ((23, 17), (30, 21)):
            self.assertLessEqual(binomial_sign_test(minimum, n - minimum)['p_value'], .05)
            self.assertGreater(binomial_sign_test(minimum - 1, n - minimum + 1)['p_value'], .05)

    def test_direction_counts_keep_optimizer_cohorts_separate(self):
        root = Path(__file__).resolve().parents[2]
        (root / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / 'scratch') as temporary:
            paths = []
            for directions in (1, 4):
                path = Path(temporary) / f'run_{directions}.txt'
                path.write_text('SPSA WINNING PARAMETERS FOR SIZE 8 (Final; mode=math)\n'
                                '#define WEIGHT_TOTAL_SCALE_S8 1400\n')
                path.with_suffix('.json').write_text(json.dumps(dict(
                    size=8, tune_mode='math', complete=True,
                    initial_parameters={'WEIGHT_TOTAL_SCALE_S8': 1452.308},
                    active_parameters=['WEIGHT_TOTAL_SCALE_S8'], config={'directions': directions})))
                paths.append(str(path))
            reports = analyze_files(paths)
        self.assertEqual(len(reports), 2)
        for report in reports:
            test = report['parameters']['WEIGHT_TOTAL_SCALE_S8']['sign_test']
            self.assertEqual(test['family_tests'], 2)
            self.assertFalse(test['significant'])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            binomial_sign_test(-1, 2)
        for values in ([float('nan')], [-.1], [1.1]):
            with self.assertRaises(ValueError):
                holm_adjust(values)
        for alpha in (0, 1, float('nan')):
            with self.assertRaises(ValueError):
                adjust_direction_tests([], alpha)


if __name__ == '__main__':
    unittest.main()
