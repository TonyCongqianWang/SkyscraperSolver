"""Tiny deterministic tests; full generation is deliberately not a test."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import random
import shutil
import sys
import tarfile
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from python_scripts.dataset_generation import artifacts, difficulty, measurement, pipeline
from python_scripts.dataset_generation.__main__ import parser, validate
from python_scripts.dataset_generation.common import Cache, digest, key, modes, sha256, symmetries

HAS_GENERATOR = importlib.util.find_spec('numba') is not None and importlib.util.find_spec('numpy') is not None


def random_clue(rng, size):
    return ' '.join(str(rng.randrange(1, size + 1)) for _ in range(size * 4))


class DatasetTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / 'scratch')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_default_cli_and_invalid_options(self):
        args = parser().parse_args(['run'])
        self.assertEqual(args.sizes, [8, 9])
        self.assertEqual((args.train_count, args.validation_count), (10000, 1000))
        self.assertEqual(args.difficulty_mix, [.2, .5, .3])
        self.assertEqual(args.timeout, 8)
        for options in (['--train-count', '9999'], ['--difficulty-mix', '.2', '.4', '.3'],
                        ['--recheck-threshold', '8'], ['--max-workers', '0']):
            with self.subTest(options=options), self.assertRaises(ValueError):
                validate(parser().parse_args(['run', *options]))

    def test_cache_rejects_changes_but_retains_completed_rows(self):
        path = self.root / 'cache.sqlite'
        cache = Cache(path, {'solver': 'one', 'settings': {'seed': 1}})
        cache.save_measurement('first', {'nodes': 123})
        cache.close()
        cache = Cache(path, {'solver': 'one', 'settings': {'seed': 1}})
        self.assertEqual(cache.measurement('first'), {'nodes': 123})
        cache.close()
        with self.assertRaisesRegex(ValueError, 'Incompatible workspace'):
            Cache(path, {'solver': 'changed', 'settings': {'seed': 1}})

    def test_matching_quotas_and_representative_blocks(self):
        selected = {}
        validation_quotas = difficulty.quotas(100, 10, [.2, .5, .3])
        for band in difficulty.BANDS:
            selected[band] = [{'key': f'{band}_{i}', 'score': i, 'band': band}
                              for i in range(validation_quotas[band] * 11)]
        train, val = difficulty.matched_split(selected, validation_quotas, 42)
        self.assertEqual((len(train), len(val)), (100, 10))
        self.assertEqual((train, val), difficulty.matched_split(selected, validation_quotas, 42))
        self.assertFalse({r['key'] for r in train} & {r['key'] for r in val})
        from collections import Counter
        for start in range(0, 100, 10):
            self.assertEqual(Counter(row['band'] for row in train[start:start + 10]), validation_quotas)

    def test_every_symmetry_borderline_recheck_and_resume(self):
        clue = random_clue(random.Random(3), 9)
        cache = Cache(self.root / 'measurements.sqlite', {})
        self.addCleanup(cache.close)
        seen = []

        class FakeSession:
            def __init__(self, *args):
                pass

            def measure(self, variant):
                seen.append(variant)
                return {'seconds': .7, 'nodes': 100, 'solutions': None, 'status': 'ok'}

            def close(self):
                pass

        settings = {'timeout': 1, 'recheck_threshold': .6}
        with patch.object(measurement, 'Session', FakeSession):
            row = measurement.screen(clue, 9, 'binary', {}, settings, cache, threading.Event())
            count = len(seen)
            again = measurement.screen(clue, 9, 'binary', {}, settings, cache, threading.Event())
        self.assertTrue(row['accepted'])
        self.assertEqual(row, again)
        self.assertEqual(count, 1 + 2 * len(symmetries(clue)))  # warmup plus two attempts
        self.assertEqual(len(seen), count)

    def test_partial_measurements_survive_interruption(self):
        clue = random_clue(random.Random(5), 9)
        cache = Cache(self.root / 'interrupted.sqlite', {})
        self.addCleanup(cache.close)
        calls = []

        class FakeSession:
            def __init__(self, *args):
                pass

            def measure(self, variant):
                calls.append(variant)
                if len(calls) == 3:
                    raise InterruptedError('test interruption')
                return {'seconds': .1, 'nodes': 200, 'solutions': None, 'status': 'ok'}

            def close(self):
                pass

        settings = {'timeout': 1, 'recheck_threshold': .6}
        with patch.object(measurement, 'Session', FakeSession):
            with self.assertRaises(InterruptedError):
                measurement.screen(clue, 9, 'binary', {}, settings, cache, threading.Event())
            before = len(calls)
            row = measurement.screen(clue, 9, 'binary', {}, settings, cache, threading.Event())
        self.assertTrue(row['accepted'])
        self.assertNotIn(symmetries(clue)[0], calls[before:])

    def test_timeouts_failures_and_over_limit_are_rejected(self):
        clue = random_clue(random.Random(6), 9)
        for status, seconds in [('timeout', 1), ('error', .1), ('ok', 1.1)]:
            with self.subTest(status=status, seconds=seconds):
                cache = Cache(self.root / f'{status}.sqlite', {})
                class FakeSession:
                    def __init__(self, *args):
                        pass
                    def measure(self, variant):
                        return {'seconds': seconds, 'nodes': 100, 'solutions': None, 'status': status}
                    def close(self):
                        pass
                with patch.object(measurement, 'Session', FakeSession):
                    row = measurement.screen(clue, 9, 'binary', {},
                                             {'timeout': 1, 'recheck_threshold': .6}, cache, threading.Event())
                self.assertFalse(row['accepted'])
                cache.close()

    def test_bundle_rejects_path_escape(self):
        path = self.root / 'unsafe.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            entry = tarfile.TarInfo('../escape')
            entry.size = 1
            archive.addfile(entry, io.BytesIO(b'x'))
        with self.assertRaises(ValueError), artifacts.open_results(path):
            pass

    @unittest.skipUnless(HAS_GENERATOR, 'Requires generation dependencies')
    def test_seeded_generation_and_latin_square_invariants(self):
        import numpy as np
        from python_scripts.dataset_generation.generator import (
            generate_random_latin_square, generate_uniform_latin_squares,
            generate_unique_instances, seed_mcmc)
        with redirect_stdout(io.StringIO()):
            first = generate_unique_instances(8, 8, 20, 10, seed=42)
            second = generate_unique_instances(8, 8, 20, 10, seed=42)
            excluded = [tuple(map(int, key(clue).split())) for clue in first]
            fresh = generate_unique_instances(8, 8, 20, 10, seed=42, excluded_keys=excluded)
        self.assertEqual(first, second)
        self.assertFalse({key(clue) for clue in first} & {key(clue) for clue in fresh})
        seed_mcmc(1)
        squares, _ = generate_uniform_latin_squares(8, 5, generate_random_latin_square(8), 20, 10)
        for square in squares:
            for row in list(square) + list(square.T):
                self.assertEqual(set(row), set(range(1, 9)))

    @unittest.skipUnless(HAS_GENERATOR, 'Requires generation dependencies')
    def test_build_bundle_verify_resume_and_install(self):
        sizes = (8, 9)
        rng = random.Random(10)
        active = self.root / 'puzzle_bank/spsa_datasets'
        active.mkdir(parents=True)
        (self.root / 'benchmark_sets').mkdir()
        originals = {}
        for size in sizes:
            for split in ('train', 'val'):
                path = active / f'size{size}_{split}.txt'
                path.write_text(''.join(f'"{random_clue(rng, size)}"\n' for _ in range(30)))
                originals[path.name] = path.read_bytes()
        binary = self.root / 'solver'
        binary.write_text('frozen test solver')
        args = parser().parse_args(['run', '--solver', str(binary), '--work-dir', str(self.root / 'work'),
                                   '--train-count', '100', '--validation-count', '10',
                                   '--reference-count', '30', '--candidate-batch-size', '200',
                                   '--burn-in', '1', '--gap', '1', '--max-batches', '10'])
        validate(args)

        def fake_generate(size, count, *unused, seed=None, excluded_keys=()):
            rng = random.Random(seed)
            excluded = set(excluded_keys)
            rows = []
            while len(rows) < count:
                clue = random_clue(rng, size)
                canonical = tuple(map(int, key(clue).split()))
                if canonical not in excluded:
                    excluded.add(canonical)
                    rows.append(clue)
            return rows

        def fake_screen(clue, size, binary, env, settings, cache, stopped):
            canonical = key(clue)
            nodes = int(digest(canonical)[:8], 16) % 10000 + 100
            for mode in modes(size):
                for variant in symmetries(clue):
                    measurement_id = digest([size, canonical, mode, variant, 1])
                    if cache.measurement(measurement_id) is None:
                        cache.save_measurement(measurement_id, dict(
                            id=measurement_id, size=size, key=canonical, mode=mode,
                            symmetry=variant, attempt=1, seconds=.01, nodes=nodes,
                            status='ok', solutions=None))
            return dict(key=canonical, clue=clue, size=size, accepted=True, reason='accepted',
                        nodes={mode: nodes for mode in modes(size)},
                        seconds={mode: .01 for mode in modes(size)})

        with patch('python_scripts.dataset_generation.generator.generate_unique_instances', side_effect=fake_generate), \
             patch.object(pipeline, 'screen', side_effect=fake_screen), redirect_stdout(io.StringIO()):
            bundle = pipeline.run(args, self.root)
        manifest = artifacts.verify(bundle)
        self.assertEqual([8, 9], manifest['settings']['sizes'])
        for name, content in originals.items():
            self.assertEqual((active / name).read_bytes(), content)
        with patch('python_scripts.dataset_generation.generator.generate_unique_instances', side_effect=AssertionError('regenerated')), \
             patch.object(measurement, 'Session', side_effect=AssertionError('remeasured')), \
             redirect_stdout(io.StringIO()):
            pipeline.run(args, self.root)
        with redirect_stdout(io.StringIO()):
            artifacts.install(bundle, active)
            artifacts.install(bundle, active)  # idempotent / interrupted-install completion
        for name, content in originals.items():
            archived = active / 'old_versions' / manifest['version'] / name
            self.assertEqual(archived.read_bytes(), content)
            self.assertNotEqual((active / name).read_bytes(), content)
        (active / 'size8_train.txt').write_text('unrelated change')
        with self.assertRaisesRegex(ValueError, 'differs from recorded original'):
            artifacts.install(bundle, active)
        payload = self.root / 'work/results'
        (payload / 'spsa_datasets/size9_val.txt').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            artifacts.verify_directory(payload)


if __name__ == '__main__':
    unittest.main()
