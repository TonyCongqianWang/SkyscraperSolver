# Effective-depth scheduling and entropy migration

This is a draft for the iteration **after** the current release candidate is
validated and released. No SPSA campaign or performance claim accompanies it.
The baseline is freshly fetched main, `7b4fcac`.

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
node; entropy separately measures remaining domain freedom. All existing
non-root depth curves intentionally share this coordinate.

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
per-node schedule caches. Existing initial/root strategies retain their
independent constant schedules, since these were never depth curves.

Actual tree depth still selects initial/root strategies and retains all search,
transition, nesting, bound, and solution-registration semantics.

## Boundary policy

The existing schedule spline is a nonuniform Catmull/Hermite curve with knots
at `0`, `.25`, `.50`, `1`. It already evaluates the first/last cubic segment
outside `[0,1]`; it does not clamp the input. This behavior is preserved.
Alpha and effective depth are unrestricted, so tuning can extrapolate beyond
either progress signal and beyond the nominal schedule interval.

The existing nonnegative floor on schedule outputs is preserved. Integer
schedules round to nearest integer and now saturate at `INT_MAX` to avoid an
undefined conversion after extreme cubic extrapolation. Scaled global cutoffs
truncate to integers and use the same representational saturation. Double
schedules keep their existing nonnegative floor. There is no entropy-dependent
runtime cap and no runtime requirement that a pruning gate remain reachable.

## Entropy units and parameter migration

Every tunable `*_GLOBAL_MIN_ENTROPY*` is now an integer in millionths of
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

The same scaling function serves initial GAC/constraint pruning, regular and
root pruning, and extra lookahead verification for both families. The formerly
hardcoded initial `513540` becomes two tunable parameters,
`INITIAL_GAC_GLOBAL_MIN_ENTROPY` and `INITIAL_CONSTR_GLOBAL_MIN_ENTROPY`.
The initial lookahead mode's existing zero global thresholds remain zero.
All three size multipliers initialize to `1` and remain tunable; none is
anchored. `GLOBAL_ENTROPY_UNSET_BIAS_*` and its accessor, metadata, and generated
environment overrides are retired. Unset count now contributes through the
shared scheduling coordinate instead of a separate cutoff correction.

For manual recentering, multiply **all three multipliers** by a positive factor
`k` and divide **all shared global cutoff parameters**, including initial and
root parameters and all curve knots, by `k`. Effective thresholds are preserved
up to integer quantization. Apply this within the tunable bounds, or adjust the
bounds explicitly if recentering requires it. Never rescale just one family.
Old winner files containing absolute global cutoffs need this unit migration
before reuse; retired unset-bias entries no longer map to solver parameters.

## Initial reseeding and coupling

Use size 9 as the reference because it has reachable constraint cutoffs that
can be preserved. For each existing shared root value and curve knot `b`, form

```
r = b * (721.984349864311 + 50) / (721.984349864311 + 81) / 442746
seed_ppm = round(r * 1_000_000) if r <= 1 else 980000
```

The factor is the old unset correction at an empty size 9 grid; `442746` is
its exact empty entropy. Initial pruning did not have the unset correction;
its old `513540` also exceeds this reference and is seeded to `980000`.
Reachable size 9 regular constraint knots and three extra constraint knots
are preserved to within 0.22 raw entropy units before integer truncation.
Values between 98% and 100% remain intact. Reseeding is an initializer change,
not a formula that runs during solving or tuning.

Shared curves and a common size multiplier cannot simultaneously retain those
size 9 values, put every previously unreachable smaller-size value at exactly
98%, and keep the GAC families near 98%. The chosen compromise preserves the
reachable size 9 knots and seeds unreachable shared knots to 98%. Consequently,
regular constraint cutoffs in smaller sizes become roughly 75–82%, and extra
constraint cutoffs roughly 95–99%. There are no hidden size/family exceptions.
Changing a knot also changes adjacent spline segments; the entire old extra
constraint curve cannot be preserved when its first knot is reseeded.
Removing the unset correction and changing the scheduling coordinate also
intentionally changes node-specific thresholds away from this reference.

The following static summaries give **before → after percentages of exact
empty-grid entropy**. Over 100% means unreachable even on an empty grid; below
100% does not guarantee activation on a particular puzzle. Before values use
`num_unset = size²` to isolate scale and reseeding. At fewer unset cells the old
cutoffs were higher. Curve ranges sample 1,001 coordinates over `[0,1]`, including
spline overshoot, rather than reporting only knot extrema. Actual nodes need
not visit every coordinate. Initial extra verification's zero global gates
remain 0% for every size and are omitted from the tables.

| Size | Empty entropy | Initial GAC / CP | Root GAC | Root CP | Root extra GAC | Root extra CP |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 5644 | 9098.9 → 98.0% | 10124.6 → 98.0% | 11650.8 → 98.0% | 11708.8 → 98.0% | 9327.9 → 98.0% |
| 3 | 20106 | 2554.2 → 98.0% | 2819.0 → 98.0% | 3243.9 → 98.0% | 3260.1 → 98.0% | 2597.2 → 98.0% |
| 4 | 45152 | 1137.4 → 98.0% | 1241.1 → 98.0% | 1428.2 → 98.0% | 1435.3 → 98.0% | 1143.5 → 98.0% |
| 5 | 81875 | 627.2 → 98.0% | 674.7 → 98.0% | 776.4 → 98.0% | 780.3 → 98.0% | 621.6 → 98.0% |
| 6 | 131220 | 391.4 → 98.0% | 413.8 → 98.0% | 476.1 → 98.0% | 478.5 → 98.0% | 381.2 → 98.0% |
| 7 | 194089 | 264.6 → 98.0% | 274.2 → 98.0% | 315.5 → 98.0% | 317.1 → 98.0% | 252.6 → 98.0% |
| 8 | 270912 | 189.6 → 98.0% | 192.0 → 98.0% | 221.0 → 98.0% | 222.1 → 98.0% | 176.9 → 98.0% |
| 9 | 442746 | 116.0 → 98.0% | 115.4 → 98.0% | 132.8 → 98.0% | 133.4 → 98.0% | 106.3 → 98.0% |

| Size | Regular GAC | Regular CP | Extra GAC | Extra CP |
| --- | --- | --- | --- | --- |
| 2 | 8899.2–12810.3 → 98.0–98.0% | 6594.3–7234.7 → 75.1–82.4% | 9614.1–16694.9 → 98.0–98.0% | 8347.6–12865.4 → 95.1–99.0% |
| 3 | 2477.8–3566.8 → 98.0–98.0% | 1836.0–2014.3 → 75.1–82.4% | 2676.8–4648.3 → 98.0–98.0% | 2324.2–3582.1 → 95.1–99.0% |
| 4 | 1090.9–1570.4 → 98.0–98.0% | 808.4–886.9 → 75.1–82.4% | 1178.6–2046.6 → 98.0–98.0% | 1023.3–1577.1 → 95.1–99.0% |
| 5 | 593.0–853.7 → 98.0–98.0% | 439.4–482.1 → 75.1–82.4% | 640.7–1112.5 → 98.0–98.0% | 556.3–857.3 → 95.1–99.0% |
| 6 | 363.7–523.5 → 98.0–98.0% | 269.5–295.7 → 75.1–82.4% | 392.9–682.3 → 98.0–98.0% | 341.1–525.8 → 95.1–99.0% |
| 7 | 241.0–346.9 → 98.0–98.0% | 178.6–195.9 → 75.1–82.4% | 260.4–452.1 → 98.0–98.0% | 226.1–348.4 → 95.1–99.0% |
| 8 | 168.8–243.0 → 98.0–98.0% | 125.1–137.2 → 75.1–82.4% | 182.3–316.6 → 98.0–98.0% | 158.3–244.0 → 95.1–99.0% |
| 9 | 101.4–146.0 → 98.0–98.0% | 75.1–82.4 → 75.1–82.4% | 109.6–190.3 → 98.0–98.0% | 95.1–146.6 → 95.1–99.0% |

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
integer saturation, production routing, entropy normalization, all scaling
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
