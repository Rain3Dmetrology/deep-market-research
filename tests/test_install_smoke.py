import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerSmoke(unittest.TestCase):
    def test_native_install_and_drift(self):
        with tempfile.TemporaryDirectory(prefix="dmr-install-") as temp:
            home = Path(temp)
            base = home / ".workbuddy" / "skills"
            base.mkdir(parents=True)
            env = dict(os.environ, HOME=temp, USERPROFILE=temp, PYTHONUTF8="1")
            if os.name == "nt":
                command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "install.ps1")]
                check = "-Check"
            else:
                command = ["bash", str(ROOT / "install.sh")]
                check = "--check"

            def run(args, expected):
                proc = subprocess.run(command + args, env=env, capture_output=True,
                                      text=True, encoding="utf-8", errors="replace", timeout=90)
                self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)

            run([], 0)
            run([check], 0)
            dest = base / "deep-market-research"
            self.assertFalse(list(dest.rglob("__pycache__")))
            with (dest / "scripts/run_contract.py").open("a", encoding="utf-8") as stream:
                stream.write("\n# synthetic drift\n")
            run([check], 1)


if __name__ == "__main__":
    unittest.main()
