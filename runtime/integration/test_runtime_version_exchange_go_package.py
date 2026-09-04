import os
import shutil
import subprocess
import unittest
from pathlib import Path


GO_ROOT = Path(__file__).resolve().parent.parent / "go"


def sanitized_go_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("SOZA_RUNTIME_EXCHANGE_") or key.startswith(
            "SOZA_E3B_RUNTIME_EXCHANGE_"
        ):
            environment.pop(key, None)
    return environment


class RuntimeVersionExchangeGoPackageTest(unittest.TestCase):
    def test_non_live_go_harness_package_compiles_and_passes(self):
        go = shutil.which("go")
        self.assertIsNotNone(
            go,
            "Go 1.25+ is required to validate the package used by the actual runtime exchange runner",
        )

        completed = subprocess.run(
            [go, "test", "./livemethodintegration", "-count=1"],
            cwd=GO_ROOT,
            env=sanitized_go_environment(),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            0,
            completed.returncode,
            "actual runtime exchange Go package failed:\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
