# Effective-depth scheduling and entropy migration

This ports the methodology onto newer main while preserving four-tier pruning,
independent positive/negative lookahead and the latest tuned defaults.
No SPSA campaign or performance claim accompanies it.
The baseline is main `ad5c908`, including its 2.5× numerical rescaling
(subject to integer truncation) and subsequent tuning adjustments.

## Scheduling coordinate

For each node, with `N = size * size`:

```
d = tree.depth / N
s = (N - num_unset) / N
D = depth_warp[size](d)
S = num_set_warp[size](s)
alpha = c0 + cD*D + cS*S + cDD*D*D + cDS*D*S + cSS*S*S
effective_depth = (1 - alpha)*D + alpha*S
```

The quadratic produces the blending factor. There is no additional coordinate
spline after it. Effective depth estimates the useful lifetime of work at the
node; entropy separately measures remaining domain freedom. All parameter
schedules intentionally share this coordinate after the one-time initial
pruning pass, including nodes at actual tree depth zero.

Both warps use the existing piecewise-linear convention: fixed endpoints
`(0, 0)` and `(1, 1)`, with tunable ordinates at `.25`, `.50`, `.75`. The size
categories remain `<=7`, `8`, `9`. Both initialize to identity in every category.
The shared coefficients initialize to `(.5, .1, -.1, 0, 0, 0)` in the order above.
Neither alpha nor the warp ordinates are required to be monotone; the old depth
warp ordering constraints are removed from SPSA.

All schedule tables now contain `(physical_depth, num_set)` pairs. The lookup
index is `physical_depth * 82 + num_set`, recomputed at each pruning entry,
including entries from lookahead. A propagation assignment therefore changes
the schedule even when physical depth stays fixed. The tables occupy about
893 KiB, versus about 11 KiB previously; at most 6,724 coordinate pairs are
initialized per puzzle. This retains constant-time lookup without mutable
per-node schedule caches. There is no separate root schedule or rounded root
bucket. Actual tree depth zero uses the same table as every other node, so
propagation at the physical root can move its scheduling coordinate.

The one-time initial pruning pass remains a separate initialization action.
Actual tree depth retains all search, transition, nesting, bound, and
solution-registration semantics.

## Boundary policy

The schedule spline is a nonuniform Catmull/Hermite curve with knots at
`0`, `1/64`, `.25`, `.50`, `1`. The fixed `1/64` location targets early progress
in the same normalized coordinate for every size; before warping, it equals
one physical step at size 8, approximately 0.77 steps at size 7, and 1.27 at
size 9. This point belongs to the parameter schedules, not the progress warps.
The spline uses centered-secant tangents at interior knots and one-sided
secants at endpoints, accounting for the unequal knot spacing. Values and
first derivatives are continuous at every knot. As before, evaluation outside
`[0,1]` continues the first/last cubic segment without clamping the input.
Alpha and effective depth are unrestricted, so tuning can extrapolate beyond
either progress signal and beyond the nominal schedule interval.

The existing nonnegative floor on schedule outputs is preserved. Integer
schedules round to nearest integer and now saturate at `INT_MAX` to avoid an
undefined conversion after extreme cubic extrapolation. Scaled global cutoffs
truncate to integers and use the same representational saturation. Double
schedules keep their existing nonnegative floor. There is no entropy-dependent
runtime cap and no runtime requirement that a pruning gate remain reachable.

## Entropy units and parameter migration

Every tunable `PRUNE_MIN_ENTROPY_*_GRID*` is now an integer in millionths of
empty-grid entropy, rather than an absolute entropy count:

```
effective_cutoff = cutoff_ppm / 1_000_000
                   * global_entropy_multiplier[size]
                   * compute_max_entropy(size)
```

`compute_max_entropy` uses the actual integer cell/constraint weights and
per-domain truncation used by the domain representation. Thus the reference is
the entropy of a genuinely empty grid, including when SPSA changes the entropy
scale or the cell/constraint weight ratio. Initialization assigns this value to
both `puzzle->max_entropy` and the empty node's `remaining_entropy`, before clues
and givens are applied. Subsequent domain reductions lower `remaining_entropy`
while the maximum stays fixed, so information supplied by the puzzle already
counts as progress. The redundant full-domain initialization scan and its
helpers are removed; an independent scan remains in tests as a reference.
This simplification preserves the previous initialization values.

The same scaling function serves initial constraint pruning, the unified
node schedules, and extra lookahead constraint verification. Scheduled
constraint propagation uses `PRUNE_MIN_ENTROPY_CONSTR_PROP_GRID_*` both to
skip the pass below the scaled threshold and to recheck the current board
entropy before each line. The formerly
hardcoded initial `1283850` is controlled by the tunable
`PRUNE_MIN_ENTROPY_INITIAL_CONSTR_PROP_GRID` parameter.
The initial lookahead mode's existing zero global thresholds remain zero.
All three size multipliers initialize to `1` and remain tunable; none is
anchored. `GLOBAL_ENTROPY_UNSET_BIAS_*` and its accessor, metadata, and generated
environment overrides are retired. Unset count now contributes through the
shared scheduling coordinate instead of a separate cutoff correction.

For manual recentering, multiply **all three multipliers** by a positive factor
`k` and divide **all shared global cutoff parameters**, including initial
parameters and all five curve knots, by `k`. Effective thresholds are preserved
up to integer quantization. Apply this within the tunable bounds, or adjust the
bounds explicitly if recentering requires it. Never rescale just one family.
Old winner files containing absolute global cutoffs need this unit migration
before reuse; retired unset-bias entries no longer map to solver parameters.

For every scheduled parameter, migrate the former `ROOT_<NAME>` to
`<NAME>_P00` (coordinate 0), and the former `<NAME>_P00` to `<NAME>_P1_64`
(coordinate 1/64). The `.25`, `.50`, and `1` parameters retain their names and
values. Apply this mapping simultaneously, so a former root value is not moved
twice. All 14 remaining schedules have these five knots. The former root
parameters are now ordinary zero-knot ordinates; the root-specific routine and
metadata names are removed. The migration preserves the remaining parameter
count, and every knot remains available in the existing joint tuning mode. The ordinate values are
preserved, but the curves between them intentionally change.

## Initial reseeding and coupling

Use size 9 as the reference because it has reachable constraint cutoffs that
can be preserved. For each existing shared root value and curve knot `b`, form

```
r = b * (721.984349864311 + 50) / (721.984349864311 + 81) / 1108161
seed_ppm = round(r * 1_000_000) if r <= 1 else 980000
```

The factor is the old unset correction at an empty size 9 grid; `1108161` is
its exact empty entropy. Initial pruning did not have the unset correction;
its old `1283850` also exceeds this reference and is seeded to `980000`.
Reachable size 9 regular constraint knots and three extra constraint knots
are preserved to within 0.56 raw entropy units before integer truncation.
Values between 98% and 100% remain intact. Reseeding is an initializer change,
not a formula that runs during solving or tuning.

Shared curves and a common size multiplier cannot simultaneously retain those
size 9 values and put every previously unreachable smaller-size value at exactly
98%. The chosen compromise preserves the reachable size 9 knots and seeds
unreachable shared knots to 98%. Consequently,
constraint cutoffs become roughly 75–82% away from the zero-knot neighborhood,
with a continuous transition from the 98% zero knot; extra constraint cutoffs
remain roughly 95–99%. There are no hidden size/family exceptions.
Changing a knot also changes adjacent spline segments; neither adding the
near-root knot nor reseeding can preserve the entire old curve.
Removing the unset correction and changing the scheduling coordinate also
intentionally changes node-specific thresholds away from this reference.

The following static summaries give **before → after percentages of exact
empty-grid entropy**. Over 100% means unreachable even on an empty grid; below
100% does not guarantee activation on a particular puzzle. Before values use
`num_unset = size²` to isolate scale and reseeding. At fewer unset cells the old
cutoffs were higher. Curve ranges sample 1,001 coordinates over `[0,1]`, including
spline overshoot, rather than reporting only knot extrema. After ranges include
the zero knot in the unified schedule; former root values are also shown
separately as the before/after zero-knot comparison. Actual nodes need not visit
every coordinate. Initial extra verification's zero global gates
remain 0% for every size and are omitted from the tables.

| Size | Empty entropy | Initial CP | Root → zero CP | Root → zero extra CP |
| --- | --- | --- | --- | --- |
| 2 | 13940 | 9209.8 → 98.0% | 11792.9 → 98.0% | 9441.7 → 98.0% |
| 3 | 49698 | 2583.3 → 98.0% | 3280.9 → 98.0% | 2626.8 → 98.0% |
| 4 | 111520 | 1151.2 → 98.0% | 1445.7 → 98.0% | 1157.4 → 98.0% |
| 5 | 202300 | 634.6 → 98.0% | 785.6 → 98.0% | 628.9 → 98.0% |
| 6 | 324252 | 395.9 → 98.0% | 481.7 → 98.0% | 385.7 → 98.0% |
| 7 | 479367 | 267.8 → 98.0% | 319.4 → 98.0% | 255.7 → 98.0% |
| 8 | 677760 | 189.4 → 98.0% | 220.8 → 98.0% | 176.8 → 98.0% |
| 9 | 1108161 | 115.9 → 98.0% | 132.6 → 98.0% | 106.2 → 98.0% |

| Size | CP schedule | Extra CP |
| --- | --- | --- |
| 2 | 6674.7–7322.9 → 75.0–98.0% | 8449.4–13022.3 → 95.0–98.9% |
| 3 | 1857.0–2037.3 → 75.0–98.0% | 2350.7–3623.0 → 95.0–98.9% |
| 4 | 818.2–897.7 → 75.0–98.0% | 1035.8–1596.4 → 95.0–98.9% |
| 5 | 444.6–487.8 → 75.0–98.0% | 562.8–867.5 → 95.0–98.9% |
| 6 | 272.6–299.1 → 75.0–98.0% | 345.1–531.9 → 95.0–98.9% |
| 7 | 180.8–198.3 → 75.0–98.0% | 228.8–352.7 → 95.0–98.9% |
| 8 | 125.0–137.1 → 75.0–98.0% | 158.2–243.8 → 95.0–98.9% |
| 9 | 75.1–82.3 → 75.0–98.0% | 95.0–146.4 → 95.0–98.9% |

## Joint tuning and validation

The extern variables, metadata/defaults, winner mapping, physical/environment
serialization, and override generator include the full model. Default
`tune-mode=all` jointly exposes both warps, all six shared coefficients, the
size multiplier, every existing schedule, and initial cutoff parameters for
the chosen size. No separate campaigns are needed. Warp bounds are `.05–.95`,
without ordering constraints; coefficient bounds are `-2–2`, including zero and
negative interactions; multiplier bounds are `.1–3`; global cutoff bounds are
`0–2,000,000` ppm. These allow thresholds above empty entropy. With default
SPSA `c=.03`, warp perturbations are `.0054`, coefficient perturbations `.012`,
and multiplier perturbations `.0174` in physical units.

Focused checks cover initialization, every physical depth/set-count pair for
sizes 4–9, quadratic interactions, nonmonotone warps, extrapolated coordinates,
integer saturation, production routing at physical root and non-root nodes, exact knot
interpolation and first-derivative continuity, entropy normalization, all scaling
paths, reseeding, joint activation, and serialization/generator coverage. The
C evaluation harness runs with undefined-behavior sanitization.

Validation for this draft:

- `norminette src/`: zero errors.
- `make re`: successful with repository warning/error and optimization flags.
- `make test` with six scratch fixtures: correct enumeration, `-s 10`, and exact
  counts; includes the known two-solution regression, 576 empty order-4 Latin
  squares, and near-complete grids of sizes 4, 7, 8, 9. Four contradictory-given
  fixtures separately confirm the expected CLI rejection.
- `bash setup_and_tune.sh` without arguments: successful baseline build,
  environment-override generation/build, and unapply in a scratch copy.
- Python regression suite: all 83 tests pass.

Micromamba is unavailable in this environment; the last two repository commands
used the available solver Python virtual environment. Setup generated its
binaries and transient parameter sources in `scratch/`. No SPSA sweep, broad
benchmark, or hard-instance investigation was launched. These checks establish
bounded correctness coverage, not release or performance validation.
