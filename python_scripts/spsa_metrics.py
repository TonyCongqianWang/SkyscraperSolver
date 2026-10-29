"""Shared SPSA objective shifts for tuning and performance comparisons."""
import math

# (time in seconds, nodes); preserve the training objective for every mode.
SGM_SHIFTS = {
    (7, False): (0.002, 100.0),
    (7, True): (0.005, 1000.0),
    (8, False): (0.200, 10000.0),
    (8, True): (2.000, 100000.0),
    (9, False): (1.000, 120000.0),
    (9, True): (1.000, 120000.0),
}


def get_sgm_shifts(size, enumeration=False):
    return SGM_SHIFTS[(size, enumeration)]


def shifted_geo_mean(values, shift):
    if not values:
        return 0.0
    return math.exp(sum(math.log(max(0.0, float(x)) + shift)
                        for x in values) / len(values)) - shift
