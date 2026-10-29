#!/usr/bin/env python3
"""
fetch_kaggle_runs.py

Helper script and CLI utility for querying historical Kaggle kernel versions,
inspecting their configuration/commands, and downloading selective run artifacts
(such as SPSA winner files) directly into workspace directories as .txt files.

Usage Examples:
  # List the last 20 versions and what commands they ran:
  micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py --list 20

  # Download the last 10 Size 8 runs automatically (discovers versions & names scratch/run_s8_<00-09>.txt):
  micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py --size 8 --count 10

  # Download the last 15 Size 9 runs:
  micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py --size 9 --count 15

  # Download explicit version range:
  micromamba run -n default python3 python_scripts/fetch_kaggle_runs.py \
      --versions 656..665 --filter "*winner*.txt" --dest "scratch/run_s8_{index:02d}.txt"
"""

import os
import sys
import re
import json
import fnmatch
import argparse
import time
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

try:
    import requests
    from kaggle import api
except ImportError:
    print("Error: 'kaggle' and 'requests' packages are required.", file=sys.stderr)
    print("Please run using: micromamba run -n default python3 ...", file=sys.stderr)
    sys.exit(1)


def retry_transient(function):
    """Back off on throttling and transient network/server failures only."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        for attempt in range(5):
            try:
                return function(*args, **kwargs)
            except requests.RequestException as error:
                response = getattr(error, 'response', None)
                status = response.status_code if response is not None else None
                if attempt == 4 or (status is not None and status != 429 and status < 500):
                    raise
                time.sleep(min(30, 2 ** (attempt + 1)))
    return wrapped


def parse_kernel_arg(kernel_str):
    if "/" in kernel_str:
        parts = kernel_str.split("/")
        return parts[0], parts[1]
    return api.config_values.get("username", "tony14587"), kernel_str


@retry_transient
def get_latest_version_number(owner, slug):
    api.authenticate()
    with api.build_kaggle_client() as client:
        req = client.kernels.kernels_api_client.get_kernel.__annotations__["request"]()
        req.user_name = owner
        req.kernel_slug = slug
        resp = client.kernels.kernels_api_client.get_kernel(req)
        return resp.metadata.current_version_number


def inspect_version(owner, slug, version_num):
    api.authenticate()
    v_label = f"v{version_num}"
    with api.build_kaggle_client() as client:
        req = client.kernels.kernels_api_client.get_kernel.__annotations__["request"]()
        req.user_name = owner
        req.kernel_slug = slug
        req.version_label = v_label
        try:
            resp = client.kernels.kernels_api_client.get_kernel(req)
            run_time = resp.metadata.last_run_time if resp.metadata else None
            cmd = ""
            size = None
            if resp.blob and resp.blob.source:
                try:
                    nb = json.loads(resp.blob.source)
                    for cell in nb.get("cells", []):
                        src = cell.get("source", "")
                        if isinstance(src, list):
                            src = "".join(src)
                        for line in src.splitlines():
                            if "setup_and_tune" in line or "spsa_tune" in line:
                                cmd = line.strip()
                                m_sz = re.search(r"--size\s+(\d+)", line)
                                if m_sz:
                                    size = int(m_sz.group(1))
                except Exception:
                    pass
            return version_num, True, run_time, cmd, size
        except Exception as e:
            return version_num, False, None, str(e), None


@retry_transient
def list_version_output_files(owner, slug, version_num):
    api.authenticate()
    v_label = f"v{version_num}"
    with api.build_kaggle_client() as client:
        method = client.kernels.kernels_api_client.list_kernel_session_output
        req = method.__annotations__["request"]()
        req.user_name = owner
        req.kernel_slug = slug
        req.version_label = v_label

        all_files = []
        token = None
        while True:
            api._set_paging(req, 200, token)
            resp = client.kernels.kernels_api_client.list_kernel_session_output(req)
            if resp.files:
                all_files.extend(resp.files)
            token = resp.next_page_token
            if not token:
                break
        return all_files


@retry_transient
def download_file(url, target_path):
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    temporary = target_path + '.part'
    try:
        with requests.get(url, stream=True, timeout=(15, 120)) as response:
            response.raise_for_status()
            with open(temporary, 'wb') as output:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        output.write(chunk)
        os.replace(temporary, target_path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def parse_version_spec(spec, latest_num):
    if not spec:
        return [latest_num]
    if ".." in spec:
        start_s, end_s = spec.split("..", 1)
        start = int(start_s)
        end = latest_num if end_s.lower() == "latest" else int(end_s)
        step = 1 if start <= end else -1
        return list(range(start, end + step, step))
    if "," in spec:
        return [int(x.strip()) for x in spec.split(",")]
    if spec.lower() == "latest":
        return [latest_num]
    return [int(spec)]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch historical outputs and inspect versions from Kaggle kernels as .txt files."
    )
    parser.add_argument(
        "--kernel",
        default="tony14587/spsa-tuning",
        help="Kernel identifier in format <owner>/<kernel-slug>",
    )
    parser.add_argument(
        "--list",
        dest="list_n",
        type=int,
        metavar="N",
        help="List and inspect the last N versions",
    )
    parser.add_argument(
        "--size",
        type=int,
        choices=[7, 8, 9],
        default=None,
        help="Filter runs to a specific puzzle size (7, 8, or 9)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of matching runs to download (e.g. 10, 15, 25)",
    )
    parser.add_argument(
        "--versions",
        help="Explicit version range or list (e.g. '656..665', '665,664', or 'latest')",
    )
    parser.add_argument(
        "--filter",
        default="*winner*.txt",
        help="Glob pattern to filter output filenames (default: '*winner*.txt')",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination path template (e.g. 'scratch/run_s{size}_{index:02d}.txt'). Always saved with .txt extension.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of concurrent workers for metadata queries",
    )

    args = parser.parse_args()
    owner, slug = parse_kernel_arg(args.kernel)

    api.authenticate()
    latest_v = get_latest_version_number(owner, slug)

    if args.list_n:
        start_v = max(1, latest_v - args.list_n + 1)
        print(f"Inspecting versions v{start_v} to v{latest_v} on {owner}/{slug}...\n")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            tasks = [
                executor.submit(inspect_version, owner, slug, v)
                for v in range(start_v, latest_v + 1)
            ]
            results = [t.result() for t in tasks]

        results.sort(key=lambda x: x[0], reverse=True)
        print(f"{'Version':<10} | {'Size':<6} | {'Last Run Time (UTC)':<20} | {'Command / Configuration'}")
        print("-" * 88)
        for v_num, ok, run_time, cmd, sz in results:
            if ok:
                rt_str = str(run_time)[:19] if run_time else "N/A"
                sz_str = f"S{sz}" if sz else "-"
                print(f"v{v_num:<9} | {sz_str:<6} | {rt_str:<20} | {cmd}")
            else:
                print(f"v{v_num:<9} | ERROR: {cmd}")
        return

    # Determine target versions
    target_versions = []
    target_size = args.size

    if args.versions:
        target_versions = parse_version_spec(args.versions, latest_v)
    elif args.count is not None or args.size is not None:
        count = args.count if args.count is not None else 10
        print(f"Searching backwards from v{latest_v} for {count} runs" + (f" matching Size {args.size}" if args.size else "") + "...")
        scan_limit = max(1, latest_v - max(count * 4, 50))
        
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            tasks = [
                executor.submit(inspect_version, owner, slug, v)
                for v in range(latest_v, scan_limit - 1, -1)
            ]
            results = [t.result() for t in tasks]

        for v_num, ok, run_time, cmd, sz in results:
            if ok:
                if args.size is None or sz == args.size:
                    target_versions.append(v_num)
                    if len(target_versions) >= count:
                        break

        # Sort chronologically (oldest to newest in the batch)
        target_versions.sort()
    else:
        print("Please specify --versions, --count, or --size (or use --list N to inspect runs).", file=sys.stderr)
        sys.exit(1)

    if not target_versions:
        print("No matching versions found to download.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(target_versions)} version(s) to download: {target_versions}")

    # Set default destination pattern if not specified
    dest_template = args.dest
    if not dest_template:
        if target_size:
            dest_template = f"scratch/run_s{target_size}_{{index:02d}}.txt"
        else:
            dest_template = "scratch/run_{index:02d}.txt"

    # Always enforce .txt extension
    if not dest_template.endswith(".txt"):
        dest_template += ".txt"

    downloaded_count = 0
    for idx, v in enumerate(target_versions):
        try:
            files = list_version_output_files(owner, slug, v)
            matched = [
                f for f in files
                if fnmatch.fnmatch(os.path.basename(f.file_name), args.filter)
            ]
            if not matched:
                print(f"[v{v}] No file matched pattern '{args.filter}' (out of {len(files)} files)")
                continue

            for mf in matched:
                # Infer size from filename if not already known (e.g. spsa_winners_s8_0.txt -> 8)
                inferred_size = target_size
                if not inferred_size:
                    m = re.search(r"_s(\d+)", mf.file_name)
                    if m:
                        inferred_size = int(m.group(1))
                    else:
                        inferred_size = "x"

                target_rel = dest_template.format(
                    index=idx,
                    version=v,
                    size=inferred_size,
                    filename=os.path.basename(mf.file_name)
                )
                if not target_rel.endswith(".txt"):
                    target_rel += ".txt"

                if len(matched) > 1 and '{filename}' not in dest_template:
                    stem, _ = os.path.splitext(target_rel)
                    target_rel = f"{stem}_{os.path.basename(mf.file_name)}"
                target_full = os.path.join(ROOT_DIR, target_rel)
                download_file(mf.url, target_full)
                downloaded_count += 1
                print(f"[v{v}] Downloaded {mf.file_name} -> {target_rel}")
                # Keep provenance adjacent to the renamed winner so analysis can
                # recover historical defaults even after the repository changes.
                remote_sidecar = os.path.splitext(mf.file_name)[0] + '.json'
                sidecars = [item for item in files if item.file_name == remote_sidecar]
                for sidecar in sidecars:
                    local_sidecar = os.path.splitext(target_full)[0] + '.json'
                    download_file(sidecar.url, local_sidecar)
                    print(f"[v{v}] Downloaded metadata -> {os.path.relpath(local_sidecar, ROOT_DIR)}")
        except Exception as e:
            print(f"[v{v}] Error: {e}")

    print(f"\nDownload completed: {downloaded_count} file(s) saved to scratch/ as .txt.")


if __name__ == "__main__":
    main()
