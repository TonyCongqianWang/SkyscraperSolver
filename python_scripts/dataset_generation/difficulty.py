"""Node-ranked strata and exactly matched training/validation allocation."""
from bisect import bisect_right
import random
import statistics

from .common import BANDS, modes


def quantile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def anchors(references, size):
    if len(references) < 3:
        raise ValueError('Fewer than three reference puzzles passed runtime screening')
    distributions = {mode: sorted(row['nodes'][mode] for row in references) for mode in modes(size)}
    result = {'distributions': distributions}
    scores = [score(row, result, size) for row in references]
    result['boundaries'] = [quantile(scores, 1 / 3), quantile(scores, 2 / 3)]
    if result['boundaries'][0] >= result['boundaries'][1]:
        raise ValueError('Reference difficulty tertiles collapse; increase --reference-count')
    return result


def score(row, reference, size):
    weights = {'single': 0.25, 'enumeration': 0.75} if size == 8 else {'single': 1.0}
    return sum(weight * bisect_right(reference['distributions'][mode], row['nodes'][mode]) /
               len(reference['distributions'][mode]) for mode, weight in weights.items())


def band_for(value, reference):
    a, b = reference['boundaries']
    return 'easy' if value <= a else 'medium' if value <= b else 'hard'


def quotas(train_count, validation_count, mix):
    if train_count != validation_count * 10:
        raise ValueError('Training count must be ten times validation count for matched groups of eleven')
    counts = [validation_count * weight for weight in mix]
    if any(abs(count - round(count)) > 1e-8 for count in counts):
        raise ValueError('Each difficulty proportion must produce an integral validation quota')
    return {band: int(round(count)) for band, count in zip(BANDS, counts)}


def matched_split(selected, validation_quotas, seed):
    rng = random.Random(seed)
    blocks = [[] for _ in range(10)]
    validation = []
    for band in BANDS:
        rows = sorted(selected[band], key=lambda row: (row['score'], row['key']))
        expected = validation_quotas[band] * 11
        if len(rows) != expected:
            raise ValueError(f'{band}: expected {expected} candidates, got {len(rows)}')
        for start in range(0, expected, 11):
            group = rows[start:start + 11]
            validation.append(group.pop(rng.randrange(11)))
            rng.shuffle(group)
            for block, row in zip(blocks, group):
                block.append(row)
    for block in blocks:
        rng.shuffle(block)
    rng.shuffle(validation)
    return [row for block in blocks for row in block], validation


def distribution(rows, size):
    result = {'count': len(rows)}
    if not rows:
        return result
    for mode in modes(size):
        for metric in ('nodes', 'seconds'):
            values = [row[metric][mode] for row in rows]
            result[f'{mode}_{metric}'] = {
                'mean': statistics.mean(values), 'p50': quantile(values, .5),
                'p90': quantile(values, .9), 'p99': quantile(values, .99), 'max': max(values)}
    return result
