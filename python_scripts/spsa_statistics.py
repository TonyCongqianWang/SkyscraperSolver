"""Exact directional sign tests and Holm family-wise error control."""
import math

TUNING_SCREEN_P = 0.05


def binomial_sign_test(up, down):
    """Two-sided H0: independent non-tied runs move up/down with probability 1/2."""
    if up < 0 or down < 0:
        raise ValueError('sign counts must be nonnegative')
    count = up + down
    if not count:
        return {'non_tied_runs': 0, 'agreement': None, 'direction': None, 'p_value': 1.0}
    tail = sum(math.comb(count, k) for k in range(min(up, down) + 1))
    return {'non_tied_runs': count, 'agreement': max(up, down) / count,
            'direction': 'up' if up > down else 'down' if down > up else None,
            'p_value': min(1.0, (2 * tail) / (1 << count))}


def holm_adjust(p_values):
    """Adjust all tests in the declared family; parameter independence is not required."""
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in p_values):
        raise ValueError('p-values must be finite probabilities')
    adjusted = [1.0] * len(p_values)
    previous = 0.0
    for rank, index in enumerate(sorted(range(len(p_values)), key=p_values.__getitem__)):
        previous = max(previous, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = previous
    return adjusted


def adjust_direction_tests(rows, alpha=0.05):
    """Annotate parameter rows, correcting across every supplied parameter/cohort test."""
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError('alpha must be finite and strictly between 0 and 1')
    tests = [row['sign_test'] for row in rows]
    for test, adjusted in zip(tests, holm_adjust([test['p_value'] for test in tests])):
        test.update(p_holm=adjusted, significant=adjusted <= alpha,
                    alpha=alpha, family_tests=len(tests),
                    tuning_candidate=test['p_value'] <= TUNING_SCREEN_P)
