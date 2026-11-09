"""Check scoped assignment marking without restricting exhaustive DFS."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LookaheadMarkingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gcc"), "Requires the solver compiler")
    def test_scoped_marks_and_complete_solution_counts(self):
        (ROOT / "scratch").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "scratch") as temporary:
            binary = Path(temporary) / "lookahead_marking_test"
            sources = sorted(str(path) for path in (ROOT / "src").glob("*.c")
                             if path.name not in ("main.c", "lookahead_depth.c"))
            harness = ROOT / "python_scripts/tests/c/lookahead_marking_harness.c"
            command = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2", "-flto",
                       "-I", str(ROOT / "src"), str(harness), *sources,
                       str(ROOT / "python_scripts/tests/config/lookahead_depth_marking.c"),
                       "-o", str(binary)]
            compiled = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            result = subprocess.run([str(binary)], capture_output=True,
                                    text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
