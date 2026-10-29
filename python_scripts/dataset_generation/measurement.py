"""Runtime screening with durable per-symmetry measurements."""
import statistics
import subprocess
import time

from comparison_measurements import parse_output, read_instance, stop_process
from .common import digest, key, modes, symmetries


class Session:
    def __init__(self, binary, mode, env, timeout):
        self.timeout = timeout
        self.proc = subprocess.Popen(
            [str(binary), '-s', '0' if mode == 'enumeration' else '1', '--stdin'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env=env, bufsize=0)

    def measure(self, clue):
        start = time.perf_counter()
        try:
            self.proc.stdin.write(f'"{clue}"\n'.encode())
            self.proc.stdin.flush()
            lines, status = read_instance(self.proc, self.timeout)
            row = parse_output(lines, time.perf_counter() - start)
            if status != 'ok':
                row['status'] = status
            return row
        except (OSError, ValueError) as error:
            return {'seconds': time.perf_counter() - start, 'nodes': None,
                    'solutions': None, 'status': 'error', 'detail': str(error)}

    def close(self):
        stop_process(self.proc)


def screen(clue, size, binary, env, settings, cache, stopped):
    canonical = key(clue)
    result = {'key': canonical, 'clue': clue, 'size': size, 'accepted': False,
              'nodes': {}, 'seconds': {}}
    for mode in modes(size):
        session = None
        observed = []
        try:
            for variant in symmetries(clue):
                for attempt in (1, 2):
                    if stopped.is_set():
                        raise InterruptedError('Generation interrupted; measurements preserved')
                    measurement_id = digest([size, canonical, mode, variant, attempt])
                    row = cache.measurement(measurement_id)
                    if row is None:
                        if session is None:
                            session = Session(binary, mode, env, settings['timeout'])
                            # Warm a fresh worker, but do not use warmup for ranking/filtering.
                            session.measure(variant)
                        row = dict(session.measure(variant), id=measurement_id,
                                   size=size, key=canonical, mode=mode,
                                   symmetry=variant, attempt=attempt)
                        cache.save_measurement(measurement_id, row)
                    observed.append(row)
                    if row['status'] != 'ok' or row['seconds'] > settings['timeout']:
                        result['reason'] = row['status'] if row['status'] != 'ok' else 'over_limit'
                        return result
                    if attempt == 1 and row['seconds'] <= settings['recheck_threshold']:
                        break
            # Rank with first measurements only; rechecks only enforce runtime safety.
            result['nodes'][mode] = statistics.median(
                row['nodes'] for row in observed if row['attempt'] == 1)
            result['seconds'][mode] = statistics.median(
                row['seconds'] for row in observed if row['attempt'] == 1)
        finally:
            if session is not None:
                session.close()
    result['accepted'] = True
    result['reason'] = 'accepted'
    return result
