"""Check optional verification scheduling through real probe transitions."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LookaheadVerificationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gcc"), "Requires the solver compiler")
    def test_optional_checks_run_only_at_first_order_boundaries(self):
        (ROOT / "scratch").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "scratch") as temporary:
            binary = Path(temporary) / "lookahead_verification_test"
            sources = sorted(str(path) for path in (ROOT / "src").glob("*.c")
                             if path.name != "main.c")
            harness = ROOT / "python_scripts/tests/c/lookahead_verification_harness.c"
            command = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2",
                       "-I", str(ROOT / "src"), str(harness), *sources,
                       "-o", str(binary), "-Wl,--wrap=process_constraint",
                       "-Wl,--wrap=check_active_constr"]
            compiled = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            result = subprocess.run([str(binary)], capture_output=True,
                                    text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
