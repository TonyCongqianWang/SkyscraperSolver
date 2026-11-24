"""Paired solver measurements with explicit failures and stable instance IDs."""
import concurrent.futures
import re
import select
import subprocess
import time


def parse_output(lines, elapsed, model=None):
    text = ''.join(lines)
    nodes = re.search(r'^Nodes visited:\s*(\d+)', text, re.M)
    solutions = re.search(r'^(?:Unique )?Solutions found:\s*(\d+)',
                          text, re.M | re.I)
    result = {'seconds': elapsed, 'nodes': int(nodes[1]) if nodes else None,
              'solutions': int(solutions[1]) if solutions else None,
              'status': 'ok' if nodes and solutions else 'error'}
    if model is not None:
        from tuning_work_runtime import parse_record
        try:
            # Both CLI modes must emit the same labeled result fields.
            # WORK_COUNTERS is an independent, instrumented cross-check.
            if result['status'] != 'ok':
                raise ValueError(
                    "Missing Solutions found or Nodes visited in solver output; "
                    "rebuild the unified solver CLI")
            predicted, counter_nodes, counter_solutions = parse_record(
                text.splitlines(), model)
            if counter_nodes != result['nodes']:
                raise ValueError(
                    "WORK_COUNTERS nodes disagree with Nodes visited")
            if counter_solutions != result['solutions']:
                raise ValueError(
                    "WORK_COUNTERS solutions disagree with Solutions found")
            result['predicted_seconds'] = predicted
        except (ValueError, KeyError, TypeError) as exc:
            result['status'] = 'error'
            result['prediction_error'] = str(exc)
    return result


def read_instance(proc, timeout):
    lines = []
    deadline = time.perf_counter() + timeout
    while True:
        remaining = deadline - time.perf_counter()
        if remaining <= 0 or not select.select([proc.stdout], [], [], remaining)[0]:
            return lines, 'timeout'
        line = proc.stdout.readline()
        if not line:
            return lines, 'error'
        lines.append(line.decode('utf-8', errors='replace'))
        if lines[-1].strip() == '--- END_OF_INSTANCE ---':
            return lines, 'ok'


def stop_process(proc):
    if proc is None:
        return
    if proc.poll() is None:
        proc.kill()
    proc.communicate()


def measure_batch(binary, options, clues, env, workers=4, use_stdin=True,
                  warmup=1, timeout=10.0, model=None):
    """Return one record per input, including timeouts and malformed output."""
    if workers < 1 or warmup < 0 or timeout <= 0:
        raise ValueError('workers/timeout must be positive; warmup nonnegative')
    indexed = list(enumerate(clues))
    groups = [indexed[i::workers] for i in range(min(workers, len(indexed)))]

    def measure_group(group):
        proc = None

        def measure(clue):
            nonlocal proc
            start = time.perf_counter()
            try:
                if use_stdin:
                    if proc is None or proc.poll() is not None:
                        stop_process(proc)
                        proc = subprocess.Popen(
                            [binary, *options.split(), '--stdin'],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, bufsize=0, env=env)
                    start = time.perf_counter()
                    proc.stdin.write(f'"{clue}"\n'.encode('utf-8'))
                    proc.stdin.flush()
                    lines, status = read_instance(proc, timeout)
                else:
                    result = subprocess.run(
                        [binary, *options.split(), clue], env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, timeout=timeout)
                    lines = result.stdout.splitlines(keepends=True)
                    status = 'ok' if result.returncode == 0 else 'error'
                row = parse_output(lines, time.perf_counter() - start, model=model)
                if status != 'ok':
                    row['status'] = status
                if row['status'] != 'ok':
                    stop_process(proc)
                    proc = None
                return row
            except subprocess.TimeoutExpired:
                status = 'timeout'
            except (OSError, ValueError):
                status = 'error'
            stop_process(proc)
            proc = None
            return {'seconds': time.perf_counter() - start, 'nodes': None,
                    'solutions': None, 'status': status}

        try:
            for _ in range(warmup):
                measure(group[0][1])
            return [dict(measure(clue), index=index, clue=clue)
                    for index, clue in group]
        finally:
            stop_process(proc)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        groups_results = list(pool.map(measure_group, groups))
    return sorted((row for group in groups_results for row in group),
                  key=lambda row: row['index'])
