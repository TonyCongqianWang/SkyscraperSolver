"""Portable I/O, identities, and a durable measurement cache."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import threading

from symmetry import canonize_clue_str, get_symmetries_from_clue_str

ROOT = Path(__file__).resolve().parents[2]
BANDS = ('easy', 'medium', 'hard')


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temporary.replace(path)


def normalize(clue, size=None):
    nums = [int(x) for x in clue.strip().strip('"\'').replace(',', ' ').split()]
    if not nums or len(nums) % 4 or (size is not None and len(nums) != size * 4):
        raise ValueError('Invalid clue length')
    n = len(nums) // 4
    if any(x < 1 or x > n for x in nums):
        raise ValueError('Dataset clues must be complete, with values in 1..size')
    return ' '.join(map(str, nums))


def read_clues(path, size=None):
    return [normalize(line, size) for line in Path(path).read_text().splitlines() if line.strip()]


def key(clue):
    return ' '.join(map(str, canonize_clue_str(clue)))


def symmetries(clue):
    return list(dict.fromkeys(get_symmetries_from_clue_str(clue)))


def modes(size):
    return ('single', 'enumeration') if size == 8 else ('single',)


def timestamp():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


@contextmanager
def workspace_lock(path):
    import fcntl
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    with (path / '.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(f'Workspace is already in use: {path}') from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


class Cache:
    def __init__(self, path, identity):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS state (name TEXT PRIMARY KEY, value TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS measurements '
                        '(id TEXT PRIMARY KEY, value TEXT)')
        old = self.get('identity')
        if old is not None and old != identity:
            self.db.close()
            raise ValueError('Incompatible workspace: solver, inputs, dependencies, code or settings changed. '
                             'Choose a different --work-dir.')
        self.put('identity', identity)

    def get(self, name, default=None):
        with self.lock:
            row = self.db.execute('SELECT value FROM state WHERE name=?', (name,)).fetchone()
            return json.loads(row[0]) if row else default

    def put(self, name, value):
        with self.lock, self.db:
            self.db.execute('INSERT OR REPLACE INTO state VALUES (?,?)',
                            (name, json.dumps(value, sort_keys=True)))

    def measurement(self, identity):
        with self.lock:
            row = self.db.execute('SELECT value FROM measurements WHERE id=?', (identity,)).fetchone()
            return json.loads(row[0]) if row else None

    def save_measurement(self, identity, row):
        with self.lock, self.db:
            self.db.execute('INSERT INTO measurements VALUES (?,?)', (identity, json.dumps(row)))

    def export(self, path):
        with Path(path).open('w') as output, self.lock:
            for row, in self.db.execute('SELECT value FROM measurements ORDER BY id'):
                output.write(row + '\n')

    def close(self):
        self.db.close()
