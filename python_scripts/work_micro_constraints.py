"""Allocate fitted merged-group coefficients using independently timed costs.

The pooled NNLS regression is completed FIRST, exactly once. The calibration
groups and their regression coefficients remain unchanged. Controlled C
microbenchmarks provide costs per original counter; observed solver-section
timings provide additional relative cost evidence. No arbitrary equal-cost
fallback and no regression refit are permitted.
"""
import math
import statistics

from work_section_plausibility import TIMED_SECTIONS


def _positive(value):
    return (isinstance(value, (int, float)) and math.isfinite(value)
            and value > 0)


def _gaussian_solve(matrix, vector):
    """Small dense linear solve; group graph Laplacian anchored at member 0."""
    n = len(vector)
    a = [list(matrix[i]) + [vector[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda row: abs(a[row][k]))
        if abs(a[pivot][k]) < 1e-12:
            raise ValueError("Timing evidence does not connect all group members")
        a[k], a[pivot] = a[pivot], a[k]
        scale = a[k][k]
        for col in range(k, n + 1):
            a[k][col] /= scale
        for row in range(n):
            if row == k:
                continue
            factor = a[row][k]
            for col in range(k, n + 1):
                a[row][col] -= factor * a[k][col]
    return [a[i][-1] for i in range(n)]


def controlled_member_costs(benchmark, minimum_rounds=3,
                            max_spread=3.0):
    """Estimate every individually benchmarked operation using round means.

    Affine sections provide two separate counter costs via a per-round
    nonnegative affine fit; isolated counters use time per executed unit.
    Each accepted member must have positive, stable measurements in all
    independent rounds. No equal-weight guesses are ever inserted.
    """
    from work_section_plausibility import TIMED_SECTIONS, timed_affine_fit
    rounds = benchmark.get("rounds", 0)
    measurements = benchmark.get("raw_measurements", [])
    series = {}
    diagnostics = {}
    for record in measurements:
        if record.get("kind") == "individual":
            name = record["counter"]
            if _positive(record.get("cpu_seconds")) and _positive(record.get("units")):
                series.setdefault(name, {}).setdefault(
                    record["round"], []).append(
                        record["cpu_seconds"] / record["units"])
    for call, volume in TIMED_SECTIONS.items():
        for index in range(rounds):
            points = [r for r in measurements if r.get("kind") == "affine"
                      and r.get("section") == call
                      and r.get("round") == index]
            fitted = timed_affine_fit([
                (point["cpu_seconds"], point["calls"], point["volume"])
                for point in points])
            if fitted.get("identifiable"):
                for name, key in ((call, "sampled_call_seconds"),
                                  (volume, "sampled_volume_seconds")):
                    value = fitted.get(key)
                    if _positive(value):
                        series.setdefault(name, {}).setdefault(
                            index, []).append(value)
    costs = {}
    for name, by_round in sorted(series.items()):
        values = [statistics.median(by_round[i])
                  for i in range(rounds) if by_round.get(i)]
        spread = max(values) / min(values) if values else None
        accepted = (rounds >= minimum_rounds
                    and len(values) == rounds and spread <= max_spread)
        diagnostics[name] = {
            "status": "accepted" if accepted else "unresolved",
            "round_unit_seconds": values,
            "round_count": len(values),
            "max_over_min": spread,
            "reason": None if accepted else
                "insufficient_or_unstable_controlled_measurements",
        }
        if accepted:
            costs[name] = statistics.median(values)
    return costs, diagnostics


def _edge(a, b, ratio, source, weight, metadata=None):
    if not _positive(ratio):
        return None
    return {"a": a, "b": b, "ratio": ratio, "source": source,
            "weight": weight, "metadata": metadata or {}}


def _section_edges(summary, members):
    """Use section affine time as independent pairwise ratio evidence."""
    edges = []
    for call, volume in TIMED_SECTIONS.items():
        if call not in members or volume not in members:
            continue
        section = summary.get("sections", {}).get(call, {})
        fitted = section.get("timed_affine_fit", {})
        ratio = fitted.get("seconds_per_volume_relative_to_call")
        if fitted.get("identifiable") and _positive(ratio):
            edges.append(_edge(call, volume, ratio, "solver_section", 1.0,
                               {"observations": section.get("observations")}))
    return edges


def _solve_ratios(members, controlled_costs, section_summary):
    """Jointly use microbench and section evidence on a log-ratio graph."""
    members = list(members)
    reference = members[0]
    edges = []
    for name in members[1:]:
        if reference in controlled_costs and name in controlled_costs:
            edges.append(_edge(reference, name,
                               controlled_costs[name] / controlled_costs[reference],
                               "controlled_micro", 4.0))
    # If one operation lacks a cost estimate, use all controlled links so
    # the remaining observed operations can still form a connected graph.
    for i, left in enumerate(members):
        for right in members[i + 1:]:
            if left == reference:
                continue
            if left in controlled_costs and right in controlled_costs:
                edges.append(_edge(left, right,
                                   controlled_costs[right] / controlled_costs[left],
                                   "controlled_micro", 4.0))
    edges.extend(_section_edges(section_summary, set(members)))
    # Independently sampled per-operation timers contribute a second cost
    # estimate for every pair where both members have measurable sections.
    sections = section_summary.get("sections", {})
    for i, left in enumerate(members):
        for right in members[i + 1:]:
            a = sections.get(left, {}).get("timed_unit_seconds")
            b = sections.get(right, {}).get("timed_unit_seconds")
            if _positive(a) and _positive(b):
                edges.append(_edge(left, right, b / a,
                                   "solver_section", 1.0))
    edges = [edge for edge in edges if edge is not None]
    if len(members) == 1:
        return {reference: 1.0}, edges
    positions = {name: i for i, name in enumerate(members[1:])}
    n = len(positions)
    matrix = [[0.0] * n for _ in range(n)]
    vector = [0.0] * n
    for edge in edges:
        rhs = math.log(edge["ratio"])
        w = edge["weight"]
        ia = positions.get(edge["a"])
        ib = positions.get(edge["b"])
        if ia is not None:
            matrix[ia][ia] += w
            vector[ia] -= w * rhs
        if ib is not None:
            matrix[ib][ib] += w
            vector[ib] += w * rhs
        if ia is not None and ib is not None:
            matrix[ia][ib] -= w
            matrix[ib][ia] -= w
    values = _gaussian_solve(matrix, vector)
    result = {reference: 1.0}
    result.update({name: math.exp(values[i]) for name, i in positions.items()})
    if any(not _positive(weight) for weight in result.values()):
        raise ValueError("Nonpositive timing-derived allocation ratio")
    return result, edges


def allocate_merged_coefficients(model, training_rows, benchmark,
                                 section_summary):
    """Unmerge pooled NNLS coefficients algebraically: NEVER refit.

    Normalize each group's timing-derived member ratios so the sum of its
    contribution over the original training observations is identical to
    the already-fitted merged feature. When counts are exactly dependent,
    its prediction is preserved on every such observation.

    Missing timing evidence is an explicit unresolved error; no implicit
    equal-cost weighting is ever assigned to a multi-member group.
    """
    groups = model["collinearity"]["groups"]
    group_coefficients = model["seconds_per_count"]
    costs, cost_diagnostics = controlled_member_costs(benchmark)
    allocations = []
    flattened = {}
    errors = []
    for group in groups:
        members = list(group["members"])
        group_name = group["name"]
        coefficient = group_coefficients[group_name]
        if len(members) == 1:
            flattened[members[0]] = coefficient
            continue
        missing = sorted(set(members) - set(costs))
        if missing:
            raise ValueError(
                f"Controlled microbenchmark must resolve every member of "
                f"{group_name}; missing or unstable: {missing}")
        ratios, evidence = _solve_ratios(members, costs, section_summary)
        original_total = sum(sum(row["counters"][member]
                                 for member in members)
                             for row in training_rows)
        weighted_total = sum(sum(row["counters"][member] * ratios[member]
                                 for member in members)
                             for row in training_rows)
        if not _positive(weighted_total) or original_total <= 0:
            raise ValueError(f"No training observations for {group_name}")
        factor = coefficient * original_total / weighted_total
        assigned = {member: factor * ratios[member] for member in members}
        flattened.update(assigned)
        drift = [
            sum(assigned[member] * row["counters"][member]
                for member in members)
            - coefficient * sum(row["counters"][member] for member in members)
            for row in training_rows
        ]
        errors.extend(drift)
        allocations.append({
            "group": group_name, "members": members,
            "merged_seconds_per_count": coefficient,
            "member_cost_ratios": ratios,
            "seconds_per_original_count": assigned,
            "normalization": "training_total_contribution",
            "max_abs_training_prediction_drift_seconds":
                max(abs(value) for value in drift),
            "timing_evidence": evidence,
        })
    return {
        "method": "post_fit_timing_unmerge_no_regression_refit",
        "seconds_per_count": flattened,
        "groups": allocations,
        "controlled_counter_costs_seconds": costs,
        "controlled_counter_diagnostics": cost_diagnostics,
        "mean_abs_group_drift_seconds": (
            statistics.mean(abs(x) for x in errors) if errors else 0.0),
        "all_merged_groups_resolved": True,
    }
