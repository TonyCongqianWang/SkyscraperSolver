"""Check that the archived benchmark results refer to the exact model bytes."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CalibrationEvidenceTests(unittest.TestCase):
    def test_benchmarked_model_hashes(self):
        evidence = json.loads((ROOT / "calibration/evidence/work_calibration.validation.json").read_text())
        self.assertFalse(evidence["refreshed_model_benchmarked"])
        for path, score in evidence["scores"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                             score["sha256"])
