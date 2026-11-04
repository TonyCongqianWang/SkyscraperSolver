"""Timeout-aware paired benchmark statistics and compact reporting."""
import math
import statistics

from spsa_metrics import shifted_geo_mean

DEFAULT_TIMEOUT = 10.0
DEFAULT_TIMEOUT_PENALTY = 4.0
DEFAULT_WIN_TOLERANCE = 0.10
ARMS = ('Baseline', 'Optimized')


def validate_policy(timeout, penalty, tolerance):
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('timeout must be finite and positive')
    if not math.isfinite(penalty) or penalty < 1:
        raise ValueError('timeout penalty must be finite and at least 1')
    if not math.isfinite(timeout * penalty):
        raise ValueError('penalized timeout must be finite')
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('win tolerance must be finite and nonnegative')


def charged_seconds(row, timeout, penalty):
    if row.get('status', 'ok') == 'timeout':
        return timeout * penalty
    if row.get('status', 'ok') == 'ok':
        return row['seconds']
    return None


def summarize(rows, shifts, node_rows=None, timeout=DEFAULT_TIMEOUT,
              timeout_penalty=DEFAULT_TIMEOUT_PENALTY):
    """Time covers all ok/timeout rows; nodes cover a common solved subset."""
    times = [charged_seconds(row, timeout, timeout_penalty) for row in rows]
    times = [value for value in times if value is not None]
    if node_rows is None:
        node_rows = [row for row in rows if row.get('status', 'ok') == 'ok']
    nodes = [row['nodes'] for row in node_rows]
    return {
        'total_nodes': sum(nodes) if nodes else None,
        'sgm_nodes': shifted_geo_mean(nodes, shifts[1]) if nodes else None,
        'total_time': sum(times) if times else None,
        'sgm_time': shifted_geo_mean(times, shifts[0]) if times else None,
    }


def pair_outcome(base, optimized, tolerance):
    """A solved instance beats a timeout; two timeouts give neither a win."""
    if any(row['status'] not in ('ok', 'timeout') for row in (base, optimized)):
        return 'error'
    if base['status'] == optimized['status'] == 'timeout':
        return 'both_timeout'
    if base['status'] == 'timeout':
        return 'Optimized'
    if optimized['status'] == 'timeout':
        return 'Baseline'
    if (base['solutions'] is not None and optimized['solutions'] is not None
            and base['solutions'] != optimized['solutions']):
        return 'mismatch'
    fast, slow = sorted((base['seconds'], optimized['seconds']))
    if slow <= fast * (1 + tolerance):
        return 'tie'
    return 'Baseline' if base['seconds'] < optimized['seconds'] else 'Optimized'


def round_statistics(measured, shifts, timeout, penalty, tolerance):
    base, optimized = (measured[arm] for arm in ARMS)
    pairs = list(zip(base, optimized))
    paired = [(b, o) for b, o in pairs if b['status'] == o['status'] == 'ok']
    known = [(b, o) for b, o in paired
             if b['solutions'] is not None and o['solutions'] is not None]
    failures = {arm: {status: sum(row['status'] == status for row in rows)
                      for status in ('timeout', 'error')}
                for arm, rows in measured.items()}
    outcomes = [dict(index=b['index'], winner=pair_outcome(b, o, tolerance))
                for b, o in pairs]
    counts = {label: sum(row['winner'] == label for row in outcomes)
              for label in (*ARMS, 'tie', 'both_timeout', 'error', 'mismatch')}
    return {
        'paired_count': len(paired), 'failures': failures,
        'solution_count_pairs': len(known),
        'solution_mismatches': counts['mismatch'],
        'instance_outcomes': outcomes, 'outcomes': counts,
        'near_best_wins': {arm: counts[arm] + counts['tie'] for arm in ARMS},
        'results': {arm: summarize(measured[arm], shifts,
                                  [pair[i] for pair in paired], timeout, penalty)
                    for i, arm in enumerate(ARMS)},
    }


def metric_summary(baseline, optimized):
    pairs = [(b, o) for b, o in zip(baseline, optimized) if b is not None and o is not None]
    if not pairs:
        return dict(baseline=None, optimized=None, diff_pct=None, diff_range_pct=None)
    b, o = zip(*pairs)
    diffs = [(y - x) / x * 100 for x, y in pairs if x]
    return {'baseline': statistics.median(b), 'optimized': statistics.median(o),
            'diff_pct': statistics.median(diffs) if diffs else None,
            'diff_range_pct': [min(diffs), max(diffs)] if diffs else None}


def format_number(value):
    return f'{value:,.6g}' if value is not None else 'n/a'


def count_summary(values):
    return {'median': statistics.median(values), 'range': [min(values), max(values)]}


def format_count(summary):
    low, high = summary['range']
    return f"{summary['median']:g} [{low:g}–{high:g}]"


def print_summary(rounds, log_print, penalty, tolerance):
    """Report per-round medians/ranges, never treat repeats as new puzzles."""
    summary = {}
    metrics = [('total_nodes', 'Total Nodes (paired solved)'),
               ('sgm_nodes', 'SGM Nodes (paired solved)'),
               ('total_time', f'PAR-{penalty:g} Total Time'),
               ('sgm_time', f'PAR-{penalty:g} SGM Time')]
    log_print('| Metric | Baseline (median) | Optimized (median) | Median paired diff | Diff range |')
    log_print('|---|---|---|---|---|')
    for key, title in metrics:
        item = metric_summary(*[[r['results'][arm][key] for r in rounds] for arm in ARMS])
        summary[key] = item
        diff = f"{item['diff_pct']:+.3f}%" if item['diff_pct'] is not None else 'n/a'
        limits = item['diff_range_pct']
        span = f'{limits[0]:+.3f}% to {limits[1]:+.3f}%' if limits else 'n/a'
        log_print(f"| **{title}** | {format_number(item['baseline'])} | "
                  f"{format_number(item['optimized'])} | {diff} | {span} |")
    counts = {}
    for arm in ARMS:
        counts[arm] = {
            'solved': count_summary([r['solved'][arm] for r in rounds]),
            'timeouts': count_summary([r['failures'][arm]['timeout'] for r in rounds]),
            'errors': count_summary([r['failures'][arm]['error'] for r in rounds]),
            'wins': count_summary([r['outcomes'][arm] for r in rounds]),
            'near_best_wins': count_summary([r['near_best_wins'][arm] for r in rounds]),
        }
    log_print('\nCounts per round: median [minimum–maximum]; repeats are not additional instances.')
    log_print('| Outcome | Baseline | Optimized |')
    log_print('|---|---|---|')
    for key, title in [('solved', 'Solved'), ('timeouts', 'Timeouts'), ('errors', 'Errors'),
                       ('wins', f'Wins (>{tolerance:.0%} faster or sole solve)'),
                       ('near_best_wins', f'Within {tolerance:.0%} of fastest solved')]:
        log_print(f'| {title} | {format_count(counts[ARMS[0]][key])} | '
                  f'{format_count(counts[ARMS[1]][key])} |')
    shared = {key: count_summary([r[key] if key == 'paired_count' else r['outcomes'][key]
                                 for r in rounds])
              for key in ('paired_count', 'tie', 'both_timeout')}
    for key, title in [('paired_count', 'Node pairs completed by both'),
                       ('tie', 'Timing ties'), ('both_timeout', 'Both timed out (no win)')]:
        log_print(f"{title}: {format_count(shared[key])}")
    return summary, dict(arms=counts, **shared)
