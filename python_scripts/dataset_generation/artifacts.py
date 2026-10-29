"""Independent result verification, portable bundles, and explicit installation."""
from collections import Counter
from contextlib import contextmanager
import json
import math
from pathlib import Path, PurePosixPath
import shutil
import statistics
import tarfile
import tempfile

from .common import (BANDS, ROOT, atomic_json, digest, key, modes, read_clues,
                     sha256, symmetries, workspace_lock)
from .difficulty import band_for, quotas, score


def safe_relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError(f'Unsafe artifact path: {name}')
    return path


@contextmanager
def open_results(source):
    source = Path(source).resolve()
    if source.is_dir():
        yield source
        return
    scratch = ROOT / 'scratch'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch, prefix='dataset_verify_') as temporary:
        target = Path(temporary)
        with tarfile.open(source, 'r:gz') as archive:
            names = set()
            for member in archive.getmembers():
                safe_relative(member.name)
                if member.name in names or not member.isfile():
                    raise ValueError('Bundle must contain distinct regular files only')
                names.add(member.name)
                path = target / member.name
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as incoming, path.open('wb') as output:
                    shutil.copyfileobj(incoming, output)
        yield target


def verify_directory(directory):
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['schema_version'] != 1:
        raise ValueError('Unsupported dataset manifest version')
    for relative, expected in manifest['files'].items():
        safe_relative(relative)
        path = directory / relative
        if path.is_symlink() or not path.is_file() or sha256(path) != expected:
            raise ValueError(f'Artifact checksum mismatch: {relative}')
    files = {path.relative_to(directory).as_posix() for path in directory.rglob('*') if path.is_file()}
    if files != set(manifest['files']) | {'manifest.json'}:
        raise ValueError('Unexpected or missing artifact files')
    settings = manifest['settings']
    validation_quotas = quotas(settings['train_count'], settings['validation_count'], settings['difficulty_mix'])
    instances = json.loads((directory / 'instances.json').read_text())
    reports = json.loads((directory / 'report.json').read_text())
    selected = {}
    for size in settings['sizes']:
        for split in ('train', 'val'):
            for row in instances[str(size)][split]:
                if row['size'] != size or row['key'] != key(row['clue']) or not row['accepted']:
                    raise ValueError('Invalid selected-instance identity')
                identity = (size, row['key'])
                if identity in selected:
                    raise ValueError('Duplicate or train/validation symmetry overlap')
                selected[identity] = row
    with (directory / 'excluded_keys.jsonl').open() as source:
        for line in source:
            row = json.loads(line)
            if (row['size'], row['key']) in selected:
                raise ValueError('New dataset overlaps existing datasets or benchmarks')
    observed = {}
    with (directory / 'measurements.jsonl').open() as source:
        for line in source:
            row = json.loads(line)
            identity = (row['size'], row['key'])
            if identity not in selected:
                continue
            measurement_key = (*identity, row['mode'], row['symmetry'], row['attempt'])
            if measurement_key in observed:
                raise ValueError('Duplicate measurement identity')
            if row['id'] != digest(list(measurement_key)):
                raise ValueError('Measurement identity checksum mismatch')
            if (row['status'] != 'ok' or not math.isfinite(row['seconds']) or
                    row['seconds'] < 0 or row['seconds'] > settings['timeout'] or
                    not isinstance(row['nodes'], int) or row['nodes'] < 0):
                raise ValueError('Selected instance has a failed or over-limit measurement')
            observed[measurement_key] = row
    for (size, canonical), row in selected.items():
        for mode in modes(size):
            first = []
            for variant in symmetries(row['clue']):
                measurement_key = (size, canonical, mode, variant, 1)
                if measurement_key not in observed:
                    raise ValueError('Missing required symmetry/mode measurement')
                measurement = observed[measurement_key]
                first.append(measurement)
                if measurement['seconds'] > settings['recheck_threshold']:
                    if (*measurement_key[:-1], 2) not in observed:
                        raise ValueError('Missing borderline runtime recheck')
            if (row['nodes'][mode] != statistics.median(item['nodes'] for item in first) or
                    row['seconds'][mode] != statistics.median(item['seconds'] for item in first)):
                raise ValueError('Instance metrics disagree with raw measurements')
        reference = reports[str(size)]['anchors']
        expected_score = score(row, reference, size)
        if row['score'] != expected_score or row['band'] != band_for(expected_score, reference):
            raise ValueError('Incorrect difficulty classification')
    for size in settings['sizes']:
        for split, factor in (('train', 10), ('val', 1)):
            rows = instances[str(size)][split]
            expected_count = settings['train_count' if split == 'train' else 'validation_count']
            if len(rows) != expected_count:
                raise ValueError('Incorrect dataset row count')
            clues = read_clues(directory / f'spsa_datasets/size{size}_{split}.txt', size)
            if clues != [row['clue'] for row in rows]:
                raise ValueError('Dataset text does not match instance metadata')
            expected = {band: validation_quotas[band] * factor for band in BANDS}
            if any(Counter(row['band'] for row in rows)[band] != count for band, count in expected.items()):
                raise ValueError('Incorrect difficulty quotas')
            if split == 'train':
                for start in range(0, len(rows), settings['validation_count']):
                    block = Counter(row['band'] for row in rows[start:start + settings['validation_count']])
                    if any(block[band] != count for band, count in validation_quotas.items()):
                        raise ValueError('Training comparison block is not representative')
        # Reconstruct the exact matched-groups property, independently of file order.
        for band in BANDS:
            combined = sorted([dict(row, split=split) for split in ('train', 'val')
                               for row in instances[str(size)][split] if row['band'] == band],
                              key=lambda row: (row['score'], row['key']))
            for start in range(0, len(combined), 11):
                if Counter(row['split'] for row in combined[start:start + 11]) != {'train': 10, 'val': 1}:
                    raise ValueError('Difficulty-matched groups are not preserved')
    expected_originals = {f'size{size}_{split}.txt' for size in settings['sizes'] for split in ('train', 'val')}
    if set(manifest['originals']) != expected_originals:
        raise ValueError('Original archive is incomplete')
    safe_relative(manifest['version'])
    if '/' in manifest['version']:
        raise ValueError('Version must be a directory name')
    for name, checksum in manifest['originals'].items():
        path = directory / f'spsa_datasets/old_versions/{manifest["version"]}/{name}'
        if sha256(path) != checksum:
            raise ValueError('Original archive checksum mismatch')
    return manifest


def package(directory, destination):
    destination = Path(destination)
    temporary = destination.with_suffix('.tmp')
    with tarfile.open(temporary, 'w:gz') as archive:
        for path in sorted(Path(directory).rglob('*')):
            if path.is_file():
                archive.add(path, arcname=path.relative_to(directory).as_posix(), recursive=False)
    temporary.replace(destination)
    destination.with_suffix(destination.suffix + '.sha256').write_text(
        sha256(destination) + '  ' + destination.name + '\n')
    return destination


def verify(source):
    with open_results(source) as directory:
        manifest = verify_directory(directory)
        print(f"Verified datasets for sizes {manifest['settings']['sizes']}; version {manifest['version']}")
        return manifest


def install(source, destination=None):
    destination = Path(destination or ROOT / 'puzzle_bank/spsa_datasets').resolve()
    with open_results(source) as directory, workspace_lock(destination):
        manifest = verify_directory(directory)
        archive = destination / 'old_versions' / manifest['version']
        # Preflight every file before changing anything. A matching archive permits
        # completion of an interrupted install with a mixture of old/new files.
        for name, original_hash in manifest['originals'].items():
            current = destination / name
            new_hash = manifest['files'][f'spsa_datasets/{name}']
            if not current.is_file():
                raise ValueError(f'Missing current dataset: {name}')
            old_copy = archive / name
            if old_copy.exists() and sha256(old_copy) != original_hash:
                raise ValueError(f'Conflicting archive: {name}')
            current_hash = sha256(current)
            if current_hash != original_hash and not (
                    current_hash == new_hash and old_copy.is_file() and sha256(old_copy) == original_hash):
                raise ValueError(f'Current dataset differs from recorded original: {name}')
        archive.mkdir(parents=True, exist_ok=True)
        for name in manifest['originals']:
            old_copy = archive / name
            if not old_copy.exists():
                shutil.copy2(directory / f'spsa_datasets/old_versions/{manifest["version"]}/{name}', old_copy)
        atomic_json(archive / 'archive_manifest.json', manifest['originals'])
        for name in manifest['originals']:
            temporary = destination / (name + '.installing')
            shutil.copy2(directory / 'spsa_datasets' / name, temporary)
            temporary.replace(destination / name)
        atomic_json(destination / 'dataset_manifest.json', manifest)
        shutil.copy2(directory / 'instances.json', destination / 'instance_metadata.json')
        shutil.copy2(directory / 'report.json', destination / 'generation_report.json')
        print(f'Installed verified datasets. Original files preserved in {archive}')
