---
name: kaggle_kernel_runs
description: Inspect historical Kaggle tuning versions and execution statuses, download winner files with provenance and comparison artifacts, and prepare an auditable sample for SPSA analysis.
---

# Kaggle tuning run artifacts

Use `python_scripts/fetch_kaggle_runs.py` from the repository root. The configured
SDK environment is `micromamba run -n default python3`; network access and normal
Kaggle authentication are required. Keep downloaded artifacts and manifests under
`scratch/`. For analysis and application, follow the
[SPSA analysis skill](../spsa_analysis_and_winners/SKILL.md).

## Select and freeze the versions

```bash
micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py --list 10 --workers 2
micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py \
  --size 8 --count 10 --workers 2 --dest 'scratch/kaggle_s8/v{version}/{filename}'
```

- Default kernel: `tony14587/spsa-tuning`; override with `--kernel` as needed.
- For “last N runs,” determine the latest version once and record the exact
  version interval, size/mode commands and included files. Distinguish the latest
  submitted versions from the latest N completed tuning winners. Missing artifacts
  must not silently change the requested sample; report gaps or state a backfill.
- `--count`/`--size` select matching notebook versions, not a guarantee of that
  many downloadable final winners. Inspect the resulting coverage.
- For a frozen interval, use `--versions FIRST..LAST` or a comma-separated list
  with the actual numeric bounds. Example of a historical interval:

```bash
micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py \
  --versions 717..766 --filter '*winner*.txt' \
  --dest 'scratch/kaggle_snapshot/v{version}/{filename}'
```

Destination templates support `{index}`, `{size}`, `{version}` and `{filename}`.
Use version directories and original filenames to avoid collisions or overwriting
local winners. Preserve user-supplied files; checksum/copy them separately when
combining local and remote evidence.

## Historical API details that affect correctness

- Every historical request must set `version_label = f"v{version}"`. An unprefixed
  number can return 404. Do not assume `kaggle kernels output owner/slug/version`
  retrieves that historical version: the CLI version-label omission was observed
  in this workflow. The helper explicitly supplies it.
- `get_kernel` supplies notebook source/commands; custom UI commit titles are not
  exposed by the helper's metadata. Historical `last_run_time` responses can
  repeat the latest notebook timestamp, so do not use them to infer each historical
  session's duration or ordering. Use version IDs and recorded run provenance.
- Output listings are paginated, typically 200 files per page, and cloned repos
  have hundreds of files. Follow `next_page_token` until exhausted; an early page
  may omit all `scratch/` winners and logs.
- `get_kernel_session_status` accepts the same user/slug/version label. Record
  its status and failure message. `RUNNING` with no outputs is not a failure;
  cancellation for platform duration is distinct from a solver-instance timeout.
- Notebook status is not tuning completion. A failed or cancelled notebook can
  contain a final winner whose adjacent JSON has `complete: true`, because tuning
  finished before comparison failed. Preserve that winner for analysis. Separate
  intermediate checkpoints (`complete: false`) from final results.

## Download the evidence efficiently

The helper exposes `get_latest_version_number`, `inspect_version`,
`list_version_output_files`, and `download_file` for targeted workflows. Reuse
these instead of fetching whole output archives or reimplementing pagination.

- The winner CLI automatically downloads the adjacent JSON sidecar when present
  and distinguishes multiple winners. Winner text remains `.txt`; sidecars retain
  `.json`. Do not mistake a sparse winner for an incomplete parameter dump.
- For deeper investigation, select tuning/comparison logs, train/validation summary
  JSON and (only when needed) per-instance JSONL. Use `download_file` with their
  actual extensions; the general CLI destination is always forced to `.txt`.
  Solver binaries and large puzzle banks are usually unnecessary for winner analysis.
- Create an audit manifest with frozen selection, version, remote filenames,
  local paths/checksums, commands, status and missing artifacts. The winner CLI
  does not automatically create this full manifest. Avoid persisting signed URLs.
- Preserve metadata containing initial/default values, active parameters, seed,
  optimizer options, source revision/hashes and dataset identities. Do not infer
  historical starts from today's defaults when a sidecar or archived snapshot exists.
- Transient download/API failures are retried by the helper with bounded backoff,
  but exhausted retries and SDK-specific errors still require checking coverage.
  If throttled (429), reduce concurrency and retry only missing versions/files,
  sequentially if needed. Keep successful downloads and flush progress. Do not
  repeatedly restart an entire large batch.
- An inaccessible mamba cache lock can be avoided with
  `XDG_CACHE_HOME="$PWD/scratch/mamba_cache"`; do not alter the global environment
  just to fetch artifacts.

## Hand off to analysis

```bash
python3 python_scripts/analyze_spsa_runs.py \
  'scratch/kaggle_snapshot/v*/spsa_winners*.txt' \
  --alpha 0.05 --json scratch/kaggle_analysis.json
```

Report actual counts by size, final versus intermediate coverage, local files and
notebook statuses. Pass along script/direction-count changes, dataset identities,
provenance gaps and the comparison timeout/penalty policy. The analyzer uses
strict cohorts and exact sign tests with Holm correction; cross-version pooling
must be explicit and preserve subgroup evidence, as described in the analysis skill.
