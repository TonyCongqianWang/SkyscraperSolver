"""Independent section-timing plausibility checks for the pooled work fit.

Timing is observational: measured CPU times NEVER enter regression fitting,
regularization selection, or counter merging. A sampled section contains
exactly the sampled call count and variable-volume work done in that section.
"""
import math
import statistics

# Each instrumented begin/end covers a call plus its measured variable volume.
# Other counters are not timed and cannot receive plausibility scores yet.
TIMED_SECTIONS = {
    "cache_pair_copy_call": "cache_pair_copy",
    "line_score": "line_score_value",
    "index_copy_call": "index_copy_pair",
}


def parse_micro_lines(lines, counter_names):
    """Read optional WORK_MICRO v2 records; reject partial/mismatched records."""
    result = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line.startswith("WORK_MICRO "):
            continue
        parts = line.split()
        if len(parts) != 8 or parts[:2] != ["WORK_MICRO", "v2"]:
            raise ValueError("Unexpected or incomplete WORK_MICRO schema")
        fields = {}
        for token in parts[2:]:
            if token.count("=") != 1:
                raise ValueError("Malformed micro timing field")
            key, value = token.split("=", 1)
            if key in fields or not value.isdecimal():
                raise ValueError("Invalid micro timing counter")
            fields[key] = int(value)
        required = {"counter", "calls", "samples", "ticks",
                    "clock_ticks_per_second", "sampled_volume"}
        if set(fields) != required:
            raise ValueError("Incorrect micro timing fields")
        idx = fields["counter"]
        if idx >= len(counter_names):
            raise ValueError("Unknown micro timing counter index")
        name = counter_names[idx]
        if name not in TIMED_SECTIONS or name in seen:
            raise ValueError("Unexpected or repeated micro timing section")
        if (fields["clock_ticks_per_second"] <= 0
                or fields["samples"] > fields["calls"]):
            raise ValueError("Invalid micro timing sample counts")
        seen.add(name)
        result.append({
            "section": name, "volume_counter": TIMED_SECTIONS[name],
            "calls": fields["calls"], "samples": fields["samples"],
            "sampled_volume": fields["sampled_volume"],
            "sampled_cpu_seconds":
                fields["ticks"] / fields["clock_ticks_per_second"],
        })
    return result


def expanded_coefficients(model, counter_names):
    """Expand sums of merged counters to their original raw-counter weights."""
    weights = dict.fromkeys(counter_names, 0.0)
    seen = set()
    groups = model["collinearity"]["groups"]
    for group in groups:
        if group["aggregation"] != "sum_raw_counts":
            raise ValueError("Unsupported calibration aggregation")
        value = model["seconds_per_count"][group["name"]]
        for name in group["members"]:
            if name not in weights or name in seen:
                raise ValueError("Invalid merged work counter")
            weights[name] = value
            seen.add(name)
    return weights


def pearson(x, y):
    if len(x) < 3:
        return None
    avg_x, avg_y = statistics.mean(x), statistics.mean(y)
    dx = [v - avg_x for v in x]
    dy = [v - avg_y for v in y]
    xx = sum(v * v for v in dx)
    yy = sum(v * v for v in dy)
    if xx <= 0 or yy <= 0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / math.sqrt(xx * yy)


def timed_affine_fit(pairs):
    """Independently infer nonnegative call/volume costs from timed sections.

    Raw samples are (elapsed_seconds, sampled_calls, sampled_volume).
    This fit is NOT fed back into the calibration regression. Return null
    coefficients when the two columns cannot be distinguished.
    """
    if len(pairs) < 3:
        return {"identifiable": False, "reason": "insufficient_samples"}
    calls = [float(p[1]) for p in pairs]
    volumes = [float(p[2]) for p in pairs]
    times = [float(p[0]) for p in pairs]
    scales = [
        math.sqrt(sum(value * value for value in values) / len(values))
        for values in (calls, volumes)
    ]
    if min(scales) <= 0:
        return {"identifiable": False, "reason": "zero_feature"}
    a = [v / scales[0] for v in calls]
    b = [v / scales[1] for v in volumes]
    aa = sum(v * v for v in a)
    bb = sum(v * v for v in b)
    ab = sum(x * y for x, y in zip(a, b))
    determinant = aa * bb - ab * ab
    normalized = determinant / (aa * bb)
    if normalized < 1e-4:
        return {"identifiable": False, "reason": "collinear_sampled_volumes",
                "normalized_determinant": normalized}
    at = sum(x * y for x, y in zip(a, times))
    bt = sum(x * y for x, y in zip(b, times))
    solutions = [((at * bb - bt * ab) / determinant,
                  (bt * aa - at * ab) / determinant),
                 (max(0.0, at / aa), 0.0),
                 (0.0, max(0.0, bt / bb)),
                 (0.0, 0.0)]
    options = [(sum((time - left * x - right * y) ** 2
                    for time, x, y in zip(times, a, b)), left, right)
               for left, right in solutions if left >= 0 and right >= 0]
    _, left, right = min(options)
    call_coeff, volume_coeff = left / scales[0], right / scales[1]
    return {
        "identifiable": True,
        "sampled_call_seconds": call_coeff,
        "sampled_volume_seconds": volume_coeff,
        "seconds_per_volume_relative_to_call":
            volume_coeff / call_coeff if call_coeff > 0 else None,
        "normalized_determinant": normalized,
        "note": "Observational CPU timings include clock overhead, not fitted regression targets",
    }


def summarize_plausibility(rows, model, counter_names):
    """Compare held-out measured CPU timings to matched sampled work terms.

    Include only rows with positive samples AND measurable positive elapsed
    section CPU time. Scores are correlations of section TOTALS across
    puzzle/configuration observations, not accuracy of individual CPU costs.
    """
    weights = expanded_coefficients(model, counter_names)
    sections = {}
    for name, volume in TIMED_SECTIONS.items():
        pairs = []
        samples = 0
        missing = 0
        zero_clock = 0
        for row in rows:
            records = {r["section"]: r for r in row.get("micro_sections", [])}
            record = records.get(name)
            if record is None or not record["samples"]:
                missing += 1
                continue
            samples += record["samples"]
            measured = record["sampled_cpu_seconds"]
            if measured <= 0:
                zero_clock += 1
                continue
            estimate = (weights[name] * record["samples"]
                        + weights[volume] * record["sampled_volume"])
            pairs.append((measured, estimate, record["samples"],
                          record["sampled_volume"]))
        measured = [x[0] for x in pairs]
        predicted = [x[1] for x in pairs]
        corr = pearson(measured, predicted)
        sum_pred = sum(predicted)
        sum_measured = sum(measured)
        sections[name] = {
            "volume_counter": volume,
            "observations": len(pairs),
            "total_sampled_packages": samples,
            "unobserved_rows": missing,
            "zero_clock_rows": zero_clock,
            "measured_cpu_seconds": sum_measured,
            "model_sampled_seconds": sum_pred,
            "pearson_r": corr,
            "measured_to_model_ratio":
                sum_measured / sum_pred if sum_pred > 0 else None,
            "timed_affine_fit": timed_affine_fit(
                [(measured, count, volume)
                 for measured, _, count, volume in pairs]),
            "status": ("measurable" if corr is not None
                       else "insufficient_variation_or_timing"),
        }
    correlations = [data["pearson_r"] for data in sections.values()
                    if data["pearson_r"] is not None]
    return {
        "plausibility_score": (
            statistics.mean(correlations) if correlations else None),
        "score_definition": "unweighted mean per-section Pearson correlation",
        "scored_sections": len(correlations),
        "possible_sections": len(TIMED_SECTIONS),
        "observations": len(rows),
        "sections": sections,
        "interpretation": (
            "Correlation of observed CPU-clock section totals with fitted "
            "cost of the SAME sampled calls/volumes. Independent diagnostic "
            "only; clock overhead and CPU effects bias absolute ratios."),
    }
