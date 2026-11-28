# Persistent work calibration models

- `work_calibration.model.json`: fully allocated refreshed default for SPSA and sweep.
- `work_calibration.provisional.model.json`: exact benchmarked November 27 provisional model.
- `work_calibration.previous.model.json`: November 24 comparison model.
- `evidence/`: reported benchmark summary and complete controlled timing refresh report.

Generated reports, raw solver journals, and candidate models belong in ignored `scratch/`. Promote candidates explicitly after review.

For current use, the maintainer assumes the bundled calibrations apply to solver revision `f1b23453d46a1cc399197ea65bc340256bdb93e7`. The active model records this assumption as its source revision, preserving the originally recorded revision separately. The two benchmarked archives retain their original bytes and historical source metadata to keep the archived SHA-256 evidence valid. This is a provenance annotation, not a new calibration or benchmark.

## November 28, 2026: 36,000-observation calibration and refresh

The new pooled regression was fitted to 27,000 training observations with 9,000 held out (seed `7615041398290283439`), reaching **99.07%** clear-pair ranking accuracy (95.80% all pairs). After a provisional deployment, a fresh Kaggle comparison used the same 3,000 configuration evaluations (500 puzzles per size, two configurations each) from its seeded holdout, with identical counter traces and native timings for both models. Ranking excludes incomplete pairs and the clear-pair filter additionally excludes noise-level deltas.

| Metric | Nov 24 previous | Nov 27 provisional |
| --- | ---: | ---: |
| Clear ranking accuracy (1,296 pairs) | 98.38% | 99.38% |
| Incorrect clear rankings | 21 | 8 |
| Overall ranking accuracy (1,437 pairs) | 95.20% | 95.89% |
| MAE (ms) | 13.288 | 7.028 |
| Complete-search MAE (ms) | 6.967 | 4.374 |
| Within-puzzle MAE (ms) | 4.599 | 2.217 |
| Overall R² | 0.98633 | 0.99651 |
| Within-puzzle R² | 0.98298 | 0.99717 |
| Size 7 clear ranking | 99.31% | 99.54% |
| Size 8 clear ranking | 98.40% | 99.08% |
| Size 9 clear ranking | 97.41% | 99.53% |

The subsequent micro-only refresh resolved **9/9 merged groups** without regression refitting, using regenerated training counter observations. All 45 benchmarked counters were accepted in the initial five-round batch of 400,000 repetitions; no retry or instability remained. The three unbenchmarked counters (`domain_scan`, `dp_candidate_check`, `setup_cache_slot`) were dropped from this regression. The formerly unresolved constraint group now has measured relative cost 11.2111 (dirty entry / check call), allocated weights 2.33765 and 26.20772 ns respectively, and maximum regenerated-training prediction drift 4.44e-16 s. Zero-weight DP and copy groups are resolved algebraically, with no arbitrary timing ratios.

The **fully allocated refreshed model** is now the default at `calibration/work_calibration.model.json`. Its fitted merged coefficients and intercept are unchanged. The prior provisional model is retained byte-for-byte at `calibration/work_calibration.provisional.model.json`; the November 24 model remains at `calibration/work_calibration.previous.model.json`. The two archived model SHA-256 digests match the reported benchmark. The 99.38% benchmark applies to the archived provisional coefficients, not the refreshed default; the default's 99.07% historical score applies to the original merged regression only. Rebenchmark the refreshed default before claiming its allocated-model accuracy. Original native observations are unavailable, and regenerated CPU-limited prefixes can differ.

See `calibration/evidence/work_calibration.validation.json` for the supplied aggregate benchmark scores and `calibration/evidence/work_calibration.refresh.timing.json` for the complete controlled timing report.
