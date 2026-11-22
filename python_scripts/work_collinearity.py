"""Training-only collinearity detection and work-counter group construction.

No third-party dependencies. Merging assumes equal provisional cost per raw
work unit inside a group; individual ratios are NOT identified by this fit.
"""
import math

CORRELATION_THRESHOLD = 0.995
DEPENDENCY_TOLERANCE = 1e-3


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def standardize(values):
    """Centered unit-L2 signal; a constant column has no estimable slope."""
    avg = sum(values) / len(values)
    centered = [v - avg for v in values]
    norm = math.sqrt(dot(centered, centered))
    if norm == 0:
        return None
    return [v / norm for v in centered]


def group_name(members):
    return "+".join(sorted(members))


def aggregate(rows, members):
    return [sum(r["counters"][name] for name in members) for r in rows]


def effective_rank(signals, tolerance):
    """Pivoted, twice-reorthogonalized Gram-Schmidt; diagnostic, not an SVD."""
    basis = []
    accepted = []
    rejected = []
    for name, vector in sorted(signals.items()):
        remainder = list(vector)
        for _ in range(2):
            for _, b in basis:
                projection = dot(remainder, b)
                remainder = [x - projection * y
                             for x, y in zip(remainder, b)]
        ratio = math.sqrt(dot(remainder, remainder))
        if ratio <= tolerance:
            rejected.append({"name": name, "relative_residual": ratio})
        else:
            accepted.append({"name": name, "relative_residual": ratio})
            basis.append((name, [x / ratio for x in remainder]))
    return {"effective_rank": len(basis),
            "column_count": len(signals),
            "independent": accepted, "dependent": rejected}


def analyze_and_merge(rows, names, correlation_threshold=CORRELATION_THRESHOLD,
                      dependency_tolerance=DEPENDENCY_TOLERANCE):
    """Merge strongly dependent columns; retain originals in samples.

    Pairwise merging uses |Pearson r|. Multivariate merging uses the residual
    of a centered column after projection onto previously accepted columns.
    The merged value is always the SUM of raw counters, never a fitted ratio.
    """
    if not rows:
        raise ValueError("Collinearity analysis requires training samples")
    if not 0 < correlation_threshold <= 1:
        raise ValueError("correlation threshold must be in (0,1]")
    if not 0 < dependency_tolerance < 1:
        raise ValueError("dependency tolerance must be in (0,1)")
    names = list(names)
    signals = {}
    constants = []
    for name in names:
        values = [float(r["counters"][name]) for r in rows]
        signal = standardize(values)
        if signal is None:
            constants.append(name)
        else:
            signals[name] = signal

    parent = {name: name for name in signals}

    def find(name):
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    def union(a, b):
        a, b = find(a), find(b)
        if a == b:
            return False
        parent[max(a, b)] = min(a, b)
        return True

    events = []
    correlations = []
    active = sorted(signals)
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            r = dot(signals[a], signals[b])
            if abs(r) >= correlation_threshold:
                correlations.append({"a": a, "b": b, "pearson_r": r})
                if union(a, b):
                    events.append({"type": "pairwise", "a": a, "b": b,
                                   "pearson_r": r})

    original_rank = effective_rank(signals, dependency_tolerance)
    # Each multivariate deficiency merges the dependent group with the basis
    # groups contributing to its projection. Repeat after regrouping, because
    # summing columns changes the matrix.
    for _ in range(len(active) + 1):
        members_by_root = {}
        for name in active:
            members_by_root.setdefault(find(name), []).append(name)
        groups = {group_name(members): sorted(members)
                  for members in members_by_root.values()}
        grouped_signals = {}
        dropped_groups = []
        for group, members in sorted(groups.items()):
            signal = standardize(aggregate(rows, members))
            if signal is None:
                dropped_groups.append(group)
            else:
                grouped_signals[group] = signal
        basis = []
        merged = False
        for group, signal in sorted(grouped_signals.items()):
            remainder = list(signal)
            projections = {}
            for _ in range(2):
                for name, vector in basis:
                    value = dot(remainder, vector)
                    projections[name] = projections.get(name, 0.0) + value
                    remainder = [x - value * y
                                 for x, y in zip(remainder, vector)]
            ratio = math.sqrt(dot(remainder, remainder))
            if ratio <= dependency_tolerance and basis:
                # The dependent column is a linear combination of the basis.
                contributors = [name for name, _ in basis
                                if abs(projections.get(name, 0)) > 1e-8]
                if not contributors:
                    contributors = [basis[0][0]]
                for other in contributors:
                    for member in groups[group]:
                        union(member, groups[other][0])
                events.append({"type": "multivariate", "group": group,
                               "basis_groups": contributors,
                               "relative_residual": ratio})
                merged = True
                break
            if ratio > 0:
                basis.append((group, [x / ratio for x in remainder]))
        if not merged:
            break

    final_members = {}
    for name in active:
        final_members.setdefault(find(name), []).append(name)
    final_groups = []
    constant_groups = []
    for members in sorted((sorted(m) for m in final_members.values())):
        name = group_name(members)
        if standardize(aggregate(rows, members)) is None:
            constant_groups.append({"name": name, "members": members})
        else:
            final_groups.append({"name": name, "members": members,
                                 "aggregation": "sum_raw_counts"})
    final_signals = {
        group["name"]: standardize(aggregate(rows, group["members"]))
        for group in final_groups
    }
    return {
        "method": "centered_pairwise_pearson_then_pivoted_gram_schmidt",
        "correlation_threshold": correlation_threshold,
        "dependency_tolerance": dependency_tolerance,
        "constant_counters": constants,
        "constant_merged_groups": constant_groups,
        "correlated_pairs": correlations,
        "merge_events": events,
        "groups": final_groups,
        "rank_before": original_rank,
        "rank_after": effective_rank(final_signals, dependency_tolerance),
        "cost_assumption": "equal per-unit cost within each merged group; provisional",
    }


def collapse_row(row, groups):
    return {"counters": {
        group["name"]: sum(row["counters"][name]
                           for name in group["members"])
        for group in groups
    }, "runtime_median_seconds": row["runtime_median_seconds"]}
