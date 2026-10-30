"""Regression coverage for solver stream failures and warmup handling."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from python_scripts.dataset_generation import measurement
from python_scripts.dataset_generation.common import Cache


class SessionTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=ROOT / 'scratch')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def session(self, source):
        binary = self.root / 'solver'
        binary.write_text(f'#!{sys.executable}\n' + source)
        binary.chmod(0o700)
        session = measurement.Session(binary, 'enumeration', os.environ.copy(), 2)
        self.addCleanup(session.close)
        return session

    def test_partial_response_timeout_discards_process(self):
        session = self.session(
            "import sys,time\nsys.stdin.readline()\n"
            "print('diagnostic',file=sys.stderr,flush=True)\n"
            "print('Nodes visited: 123',flush=True)\ntime.sleep(60)\n"
            "print('--- END_OF_INSTANCE ---',flush=True)\n")
        row = session.measure('input')
        self.assertEqual(row['status'], 'timeout')
        self.assertIn('Nodes visited: 123', row['stdout'])
        self.assertIn('diagnostic', row['stderr'])
        self.assertIsNotNone(row['returncode'])
        self.assertIsNotNone(session.proc.poll())
        with self.assertRaisesRegex(RuntimeError, 'closed session'):
            session.measure('next input')

    def test_malformed_response_discards_process(self):
        session = self.session(
            "import sys,time\nsys.stdin.readline()\n"
            "print('--- END_OF_INSTANCE ---',flush=True)\ntime.sleep(60)\n")
        row = session.measure('input')
        self.assertEqual(row['status'], 'error')
        self.assertIn('END_OF_INSTANCE', row['stdout'])
        self.assertTrue(session.closed)

    def test_successful_session_can_be_reused(self):
        session = self.session(
            "import sys\nfor line in sys.stdin:\n"
            " print('Nodes visited: 123')\n"
            " print('--- END_OF_INSTANCE ---',flush=True)\n")
        for _ in range(3):
            self.assertEqual(session.measure('input')['nodes'], 123)
            self.assertFalse(session.closed)

    def test_failed_warmup_is_cached_without_another_request(self):
        clue = ' '.join(['1'] * 36)
        for status in ('timeout', 'error'):
            with self.subTest(status=status):
                cache = Cache(self.root / f'{status}.sqlite', {})
                self.addCleanup(cache.close)
                with patch.object(measurement, 'Session') as factory:
                    session = factory.return_value
                    session.measure.return_value = dict(
                        status=status, seconds=1, nodes=None, solutions=None,
                        returncode=-9, stderr='diagnostic', stdout='partial')
                    settings = {'timeout': 1, 'recheck_threshold': .6}
                    result = measurement.screen(clue, 9, 'solver', {}, settings,
                                                cache, threading.Event())
                    self.assertFalse(result['accepted'])
                    self.assertEqual(result['reason'], status)
                    session.measure.assert_called_once()
                    session.close.assert_called_once()
                    rows = [json.loads(row[0]) for row in
                            cache.db.execute('SELECT value FROM measurements')]
                    self.assertEqual(len(rows), 1)
                    self.assertEqual(rows[0]['phase'], 'warmup')
                    self.assertEqual(rows[0]['stderr'], 'diagnostic')
                    measurement.screen(clue, 9, 'solver', {}, settings,
                                       cache, threading.Event())
                    factory.assert_called_once()


if __name__ == '__main__':
    unittest.main()
