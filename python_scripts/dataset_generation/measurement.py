"""Runtime screening with durable per-symmetry measurements."""
import statistics
import subprocess
import tempfile
import time

from comparison_measurements import parse_output, read_instance, stop_process
from .common import ROOT, digest, key, modes, symmetries


class Session:
    def __init__(self, binary, mode, env, timeout):
        self.timeout = timeout
        (ROOT / 'scratch').mkdir(exist_ok=True)
        self.stderr = tempfile.TemporaryFile(dir=ROOT / 'scratch')
        self.closed = False
        try:
            self.proc = subprocess.Popen(
                [str(binary), '-s', '0' if mode == 'enumeration' else '1', '--stdin'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr,
                env=env, bufsize=0)
        except OSError:
            self.stderr.close()
            raise

    def measure(self, clue):
        start = time.perf_counter()
        if self.closed:
            raise RuntimeError('Cannot measure using a failed or closed session')
        lines = []
        try:
            self.proc.stdin.write(f'"{clue}"\n'.encode())
            self.proc.stdin.flush()
            lines, status = read_instance(self.proc, self.timeout)
            row = parse_output(lines, time.perf_counter() - start)
            if status != 'ok':
                row['status'] = status
        except (OSError, ValueError) as error:
            row = {'seconds': time.perf_counter() - start, 'nodes': None,
                   'solutions': None, 'status': 'error', 'detail': str(error)}
        if row['status'] != 'ok':
            self.close()
            row.update(returncode=self.proc.returncode, stderr=self.error_output,
                       stdout=''.join(lines))
        return row

    def close(self):
        if self.closed:
            return
        stop_process(self.proc)
        self.stderr.seek(0)
        self.error_output = self.stderr.read().decode('utf-8', errors='replace')
        self.stderr.close()
        self.closed = True


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
                            warmup = session.measure(variant)
                            if warmup['status'] != 'ok' or warmup['seconds'] > settings['timeout']:
                                row = dict(warmup, phase='warmup')
                            else:
                                row = session.measure(variant)
                        else:
                            row = session.measure(variant)
                        row = dict(row, id=measurement_id,
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
