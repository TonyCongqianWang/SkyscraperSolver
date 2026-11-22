"""Ranking diagnostics that distinguish configuration deltas from timing noise.

Pairwise comparisons are only made within the same puzzle and solve mode.
The confidence filter is a heuristic based on repeated native timings,
not a statistical significance test with guaranteed coverage.
"""
import math
import statistics


def timing_standard_error(row):
    """Approximate standard error of the measured median in seconds."""
    times = row.get("native_times_seconds", [])
    if len(times) < 2:
        return 0.0
    sigma = statistics.stdev(times)
    # Standard normal approximation for a sample median.
    return 1.253314 * sigma / math.sqrt(len(times))


def ranking_diagnostics(rows, predict, noise_z=2.0,
                        min_delta_seconds=5e-5):
    """Aggregate comparisons in O(puzzles * configurations**2)."""
    groups = {}
    for row in rows:
        identity = row.get("identity", (row.get("dataset"), row.get("line")))
        key = (row.get("size"), identity, row.get("max_solutions"))
        groups.setdefault(key, []).append(row)
    pairs = confident = correct = confident_correct = 0
    per_puzzle = []
    within_errors = []
    within_actual = []
    within_predicted = []
    excluded_noise = 0
    for group in groups.values():
        if len(group) < 2:
            continue
        actuals = [float(r["runtime_median_seconds"]) for r in group]
        estimates = [float(predict(r)) for r in group]
        actual_center = statistics.mean(actuals)
        estimate_center = statistics.mean(estimates)
        within_errors.extend((p - estimate_center) - (a - actual_center)
                             for p, a in zip(estimates, actuals))
        within_actual.extend(a - actual_center for a in actuals)
        within_predicted.extend(p - estimate_center for p in estimates)
        group_pairs = group_correct = group_confident = group_conf_correct = 0
        for i, a in enumerate(group):
            for j in range(i + 1, len(group)):
                b = group[j]
                if a["configuration"] == b["configuration"]:
                    continue
                measured = actuals[i] - actuals[j]
                expected = estimates[i] - estimates[j]
                if measured == 0:
                    continue
                pairs += 1
                group_pairs += 1
                is_correct = measured * expected > 0
                correct += is_correct
                group_correct += is_correct
                threshold = max(
                    min_delta_seconds,
                    noise_z * math.hypot(
                        timing_standard_error(a), timing_standard_error(b)))
                if abs(measured) <= threshold:
                    excluded_noise += 1
                    continue
                confident += 1
                group_confident += 1
                confident_correct += is_correct
                group_conf_correct += is_correct
        per_puzzle.append({
            "comparisons": group_pairs,
            "accuracy": group_correct / group_pairs if group_pairs else None,
            "clear_comparisons": group_confident,
            "clear_accuracy": group_conf_correct / group_confident
                if group_confident else None,
        })
    if within_errors:
        centered_mae = statistics.mean(abs(e) for e in within_errors)
        norm = sum(y * y for y in within_actual)
        centered_r2 = (
            1 - sum(e * e for e in within_errors) / norm if norm else None)
    else:
        centered_mae = None
        centered_r2 = None
    valid_clear = [g["clear_accuracy"] for g in per_puzzle
                   if g["clear_accuracy"] is not None]
    return {
        "ranking_pairs": pairs,
        "ranking_accuracy": correct / pairs if pairs else None,
        "clear_ranking_pairs": confident,
        "clear_ranking_accuracy":
            confident_correct / confident if confident else None,
        "noise_excluded_pairs": excluded_noise,
        "clear_ranking_coverage": confident / pairs if pairs else None,
        "macro_clear_ranking_accuracy":
            statistics.mean(valid_clear) if valid_clear else None,
        "puzzles_with_clear_comparisons": len(valid_clear),
        "within_puzzle_mae_seconds": centered_mae,
        "within_puzzle_r2": centered_r2,
        "noise_z": noise_z, "minimum_delta_seconds": min_delta_seconds,
        "noise_model": "2x median standard errors from native repeated timings",
    }
