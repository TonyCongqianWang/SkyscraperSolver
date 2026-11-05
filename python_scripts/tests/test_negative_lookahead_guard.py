"""Guard nested negative lookahead without suppressing regular DFS."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NegativeLookaheadGuardTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gcc"), "Requires the solver compiler")
    def test_negative_guard_and_regular_branching(self):
        (ROOT / "scratch").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "scratch") as temporary:
            binary = Path(temporary) / "negative_lookahead_guard_test"
            sources = sorted(str(path) for path in (ROOT / "src").glob("*.c")
                             if path.name != "main.c")
            harness = ROOT / "python_scripts/tests/c/negative_lookahead_guard_harness.c"
            command = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2", "-flto",
                       "-I", str(ROOT / "src"), str(harness), *sources,
                       "-o", str(binary)]
            compiled = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            result = subprocess.run([str(binary)], capture_output=True,
                                    text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
