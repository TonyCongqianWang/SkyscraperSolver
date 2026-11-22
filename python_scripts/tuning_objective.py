"""Single source of truth for sweep and SPSA training objective definitions.

Predicted work is measured in seconds and uses the existing *time* log
shift/reference. The original nodes+time objective remains explicitly
selectable; its SPSA and sweep mixing policies are intentionally preserved.
"""
import math

from spsa_metrics import get_sgm_shifts, mean_log_shifted, shifted_geo_mean

MODE_WEIGHTS = {7: (1.0, 1.5), 8: (0.5, 1.5), 9: (1.0, 0.0)}
SWEEP_MODE_WEIGHTS = {7: (0.5, 1.5), 8: (0.5, 1.5), 9: (1.0, 0.0)}
REFERENCES = {
    7: ((0.005, 350.0), (0.01, 2000.0)),
    8: ((0.1, 5000.0), (1.0, 50000.0)),
    9: ((0.1, 20000.0), (0.1, 20000.0)),
}
SWEEP_TIME_WEIGHTS = {7: 0.7, 8: 0.64, 9: 0.66}
WORK = "work"
TIME_NODES = "nodes-time"  # measured wall time + search nodes, fully supported
DEFAULT_OBJECTIVE = WORK


def mode_losses(size, enumeration, predicted_or_wall_times, nodes):
    """Return centered log losses (seconds-like time, nodes) and their SGMs."""
    time_shift, node_shift = get_sgm_shifts(size, enumeration)
    time_ref, node_ref = REFERENCES[size][bool(enumeration)]
    return (
        mean_log_shifted(predicted_or_wall_times, time_shift, time_ref),
        mean_log_shifted(nodes, node_shift, node_ref),
        shifted_geo_mean(predicted_or_wall_times, time_shift),
        shifted_geo_mean(nodes, node_shift),
    )


def weighted_modes(size, values_by_mode, objective=DEFAULT_OBJECTIVE,
                   tuner="spsa"):
    """Aggregate mode losses independently of how many puzzles each has."""
    time_loss = 0.0
    nodes_loss = 0.0
    for enumeration, (times, nodes) in values_by_mode.items():
        weights = (SWEEP_MODE_WEIGHTS if
                   objective == TIME_NODES and tuner == "sweep" else MODE_WEIGHTS)
        weight = weights[size][int(bool(enumeration))]
        t, n, _, _ = mode_losses(size, enumeration, times, nodes)
        time_loss += weight * t
        nodes_loss += weight * n
    return time_loss, nodes_loss


def sweep_score(size, time_loss, nodes_loss, objective=DEFAULT_OBJECTIVE):
    if objective == WORK:
        result = time_loss
    elif objective == TIME_NODES:
        fraction = SWEEP_TIME_WEIGHTS[size]
        result = fraction * time_loss + (1.0 - fraction) * nodes_loss
    else:
        raise ValueError(f"Unknown objective: {objective}")
    if not math.isfinite(result):
        raise ValueError("Nonfinite tuning objective")
    return result


def spsa_components(time_loss, nodes_loss, objective=DEFAULT_OBJECTIVE):
    """SPSA expects two gradients; work uses one identical scalar twice.

    Keeping equal streams preserves the existing SPSA step and momentum
    clipping exactly while optimizing a single work objective.
    """
    if objective == WORK:
        return time_loss, time_loss
    if objective == TIME_NODES:
        return time_loss, nodes_loss
    raise ValueError(f"Unknown objective: {objective}")
