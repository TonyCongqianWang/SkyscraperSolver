"""Independent controlled C timings as *relative* costs inside merged groups.

Do not replace solver-runtime coefficients with microbenchmark seconds.
Microbenchmarks identify only cost *ratios*. Pooled nonnegative regression
then estimates the overall seconds-per-weighted-work coefficient.
"""
import math
import statistics


def derive_reliable_ratios(benchmark, max_spread=2.0):
    """Require three independent timed rounds and positive stable costs.

    Each operation has one fixed call term and one variable-volume term.
    All other counter pairs remain unconstrained. This is a conservative
    heuristic acceptance criterion, not a confidence interval.
    """
    from work_section_plausibility import TIMED_SECTIONS, timed_affine_fit
    measurements = benchmark.get("raw_measurements", [])
    rounds = benchmark.get("rounds", 0)
    results = {}
    ratios = {}
    for call, volume in TIMED_SECTIONS.items():
        estimates = []
        reason = None
        for round_number in range(rounds):
            points = [r for r in measurements
                      if r["section"] == call
                      and r.get("round") == round_number]
            if len(points) < 3 or any(
                    not math.isfinite(r["cpu_seconds"])
                    or r["cpu_seconds"] <= 0 for r in points):
                reason = "missing_or_nonpositive_measurements"
                break
            fitted = timed_affine_fit([
                (p["cpu_seconds"], p["calls"], p["volume"]) for p in points])
            if not fitted.get("identifiable"):
                reason = fitted.get("reason", "unidentifiable")
                break
            fixed = fitted["sampled_call_seconds"]
            variable = fitted["sampled_volume_seconds"]
            if min(fixed, variable) <= 0:
                reason = "nonpositive_fitted_cost"
                break
            ratio = variable / fixed
            if not math.isfinite(ratio) or ratio <= 0:
                reason = "invalid_ratio"
                break
            estimates.append(ratio)
        if reason is None and rounds < 3:
            reason = "requires_three_independent_rounds"
        if reason is None:
            spread = max(estimates) / min(estimates)
            if spread > max_spread:
                reason = "unstable_between_rounds"
        if reason is None:
            ratios[(call, volume)] = statistics.median(estimates)
        results[call] = {
            "volume_counter": volume,
            "status": "accepted" if reason is None else "unresolved",
            "reason": reason,
            "round_ratios": estimates,
            "ratio": statistics.median(estimates) if reason is None else None,
            "max_over_min_ratio": (
                max(estimates) / min(estimates) if estimates else None),
        }
    return {
        "ratios": ratios,
        "details": results,
        "max_round_spread": max_spread,
        "independent_rounds": rounds,
    }


def apply_micro_ratios(groups, ratios):
    """Add within-group member weights only for measured member pairs.

    Unmeasured group members keep the sum-of-counts assumption. A ratio
    does not identify members that are not both represented in the group.
    """
    applied = []
    for group in groups:
        members = set(group["members"])
        weights = {name: 1.0 for name in members}
        for (call, volume), ratio in sorted(ratios.items()):
            if call in members and volume in members:
                if not math.isfinite(ratio) or ratio <= 0:
                    raise ValueError("Nonfinite/nonpositive micro ratio")
                weights[volume] = ratio
                applied.append({
                    "group": group["name"], "call": call,
                    "volume": volume, "measured_ratio": ratio})
        if any(value != 1.0 for value in weights.values()):
            group["aggregation"] = "weighted_sum_raw_counts"
            group["member_weights"] = {
                name: weights[name] for name in group["members"]}
    return applied
