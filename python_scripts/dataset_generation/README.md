# Remote SPSA dataset generation

This workflow generates new size-8 and size-9 tuning datasets on a fresh clone.
The default run **does not replace active datasets** and does not run SPSA.
It returns one `.tar.gz` bundle to bring back for analysis and installation.

## Fresh-clone setup

Use a POSIX host (Linux or macOS), Python 3.11 or newer, GCC and Make. No Kaggle
credentials, historical solver binaries or existing scratch files are required.
The pinned NumPy/Numba versions are the versions used for generator testing.

```bash
git clone <repository-url>
cd SkyscraperSolver
python3 -m venv venv
venv/bin/python -m pip install -r python_scripts/dataset_generation/requirements.txt
PYTHON="$PWD/venv/bin/python" BUILD_JOBS=4 ./generate_spsa_datasets.sh
```

The wrapper resolves the checkout relative to itself, checks dependencies, builds
`skyscraper_solver` with Make, and calls the Python CLI. It accepts additional CLI
arguments, which override the selected defaults. `BUILD_JOBS` controls compilation;
`--max-workers` controls calibration. Build a clean baseline if using a previously
modified checkout: do not inject tuning overrides into C sources before running.

The full default calibration may take several hours. Run it in tmux/screen if
needed. Progress is flushed to stdout and `progress.json`; retain stdout with
`tee` if desired. Pressing Ctrl-C preserves cached measurements and exits nonzero.

## Selected options

- Sizes 8 and 9, each with 10,000 training and 1,000 validation puzzles.
- Easy/medium/hard mix: 20% / 50% / 30% in both splits.
- Seed 20261029, four calibration workers.
- Every distinct symmetry must complete under an eight-second ceiling. Size 8
  checks single solution and enumeration; size 9 checks single solution.
- Measurements above 6.4 seconds are checked a second time, which must also pass.
- Difficulty anchors come from a seeded sample of up to 500 old puzzles per size.
- Candidate batches of 2,000; MCMC burn-in 100,000 and sample gap 100.

```bash
./generate_spsa_datasets.sh --help
PYTHON="$PWD/venv/bin/python" ./generate_spsa_datasets.sh \
  --work-dir scratch/my_generation --max-workers 4
```

Both Python and Numba RNGs are seeded. Timings remain machine/load dependent.
The generator uses the existing cycle-switch MCMC algorithm and independent
seeded batches; it does not claim proven uniform sampling of all Latin squares.
Fresh candidates exclude symmetry equivalents of all existing SPSA dataset
versions and benchmark clue sets in the checkout. It does not add symmetry copies
to inflate instance counts. All generated puzzles come from complete Latin squares.

Difficulty uses median node counts across distinct symmetries. Size 8 combines
reference percentile ranks at 25% single / 75% enumeration; size 9 uses single
solution ranks. The old reference score tertiles define the three bands. Fewer
than three passing references or collapsed tertiles aborts with a diagnostic;
use a larger reference sample in a new workspace if necessary.

In each band, adjacent groups of eleven contribute one random validation puzzle
and ten training puzzles. Each consecutive training block of 1,000 has exactly
the chosen difficulty proportions, preserving representative prefix comparisons.
Non-default counts must retain a 10:1 training/validation ratio, and each mix
weight must give an integral validation quota. For example, 100/10 supports the
normal mix; 10/1 can use `--difficulty-mix 0 1 0` for a tiny smoke test.

## Resume and return results

Re-run the **same command** to resume. Results live by default under
`scratch/spsa_dataset_generation/`:

- `cache.sqlite`: durable per-measurement checkpoints and generated candidate batches.
- `baseline_solver`: frozen solver used for the entire run.
- `progress.json`: latest screening progress; no partial datasets are activated.
- `results/`: verified datasets, raw measurements, provenance and reports.
- `spsa_datasets_<version>.tar.gz` and its `.sha256`: the bundle to return.

Completed measurements, including failures, are reused. A measurement interrupted
before completion is repeated. Solver, source, Python/dependency, input or
sampling-setting changes refuse cache reuse; choose another `--work-dir`.
Moving an otherwise identical checkout/workspace is supported. One process owns
each workspace. The finite `--max-batches` limit defaults to 1,000; if quotas are
not filled it aborts without relaxing filters. This operational limit may be
increased while resuming the same workspace.

The bundle includes all four new text files; the original files byte-for-byte
under `spsa_datasets/old_versions/<version>/`; checksums; seeds and source/solver
identity; per-instance and per-symmetry measurements; exclusion identities;
filtering counts; and `report.md`/`report.json` with node and runtime distributions.

Return the `.tar.gz` and its `.sha256` file. The cache and executable are not
needed to inspect or install completed results.

## CLI commands

Run from the checkout root. `verify` and `install` only require the Python standard
library; NumPy and Numba are imported only for generation.

```bash
python3 -m python_scripts.dataset_generation generate \
  --size 8 --count 2000 --seed 42 --output scratch/candidates.txt
python3 -m python_scripts.dataset_generation run --help
python3 -m python_scripts.dataset_generation verify scratch/spsa_datasets_VERSION.tar.gz
python3 -m python_scripts.dataset_generation install scratch/spsa_datasets_VERSION.tar.gz
```

`verify` checks checksums, exact quotas, symmetry exclusions, split separation,
representative training blocks, difficulty-matched groups, classification,
required symmetry/mode measurements, rechecks, and original archive integrity.
It verifies stored evidence without rerunning the expensive solver measurements.
The current stdin protocol reports nodes but not solution counts; dataset validity
comes from generating complete Latin squares and checking solver output, rather
than requiring unique solutions.

`install` is explicit. It verifies results and current-original checksums before
writing, archives original files, and atomically replaces individual dataset files.
A partially interrupted installation can be safely completed by rerunning it:
already replaced files are accepted only with the matching preserved archive.
Existing conflicting archives or unrelated current datasets cause an error.
Use `--destination` only to install into another dataset directory.

The old `python_scripts/generate_instances.py` entrypoint and its options remain
available, now with optional `--seed`. Reusable implementation is in this package.

## Tests

```bash
venv/bin/python -m unittest discover -s python_scripts/tests -v
bash -n generate_spsa_datasets.sh
```

Tests use tiny fixtures and isolated workspaces. The full dataset run is intended
for the remote instance, not as a local test.
