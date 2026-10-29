"""Portable, self-contained provenance saved beside every SPSA winner."""
import hashlib
import json
from pathlib import Path
import subprocess
import platform
import sys
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent.parent


def clue_identity(clues):
    """Hash the ordered dataset actually loaded, independent of its location."""
    content = ''.join(f'{clue}\n' for clue in clues).encode('utf-8')
    return {'count': len(clues), 'sha256': hashlib.sha256(content).hexdigest()}


def build_run_metadata(args, datasets, parameters, active_names, workers,
                       initial_parameters):
    def git(*arguments):
        try:
            return subprocess.check_output(
                ['git', *arguments], cwd=ROOT_DIR, text=True,
                stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    revision = git('rev-parse', 'HEAD')
    status = git('status', '--porcelain', '--untracked-files=no')
    sources = {}
    for pattern in ('src/*.c', 'src/*.h', 'python_scripts/*.py', 'Makefile'):
        for path in sorted(ROOT_DIR.glob(pattern)):
            sources[path.relative_to(ROOT_DIR).as_posix()] = hashlib.sha256(
                path.read_bytes()).hexdigest()
    return {
        'schema_version': 1,
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'size': args.size,
        'tune_mode': args.tune_mode,
        'seed': args.seed,
        'revision': revision,
        'tracked_worktree_dirty': bool(status) if status is not None else None,
        'source_sha256': sources,
        'python_version': sys.version,
        'platform': platform.platform(),
        'solver_sha256': hashlib.sha256((ROOT_DIR / 'skyscraper_solver').read_bytes()).hexdigest()
                         if (ROOT_DIR / 'skyscraper_solver').is_file() else None,
        'config': {key: value for key, value in vars(args).items() if key != 'log'},
        'workers': workers,
        'batch_size': args.batch_size if args.batch_size is not None else
                      {7: 128, 8: 32, 9: 256}[args.size],
        'defaults': {row[0]: row[3] for row in parameters},
        'initial_parameters': initial_parameters,
        'active_parameters': sorted(active_names),
        'parameter_metadata': [
            {'name': name, 'min': low, 'max': high, 'default': default,
             'type': kind.__name__, 'perturb_scale': scale}
            for name, low, high, default, kind, scale in parameters],
        'datasets': {key: clue_identity(clues)
                     for key, clues in sorted(datasets.items())},
    }


def save_run_metadata(winners_path, metadata, label):
    payload = dict(metadata, label=label, complete=label.startswith('Final'))
    path = Path(winners_path).with_suffix('.json')
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)
