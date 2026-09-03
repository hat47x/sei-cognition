import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "run_runtime_version_exchange_with_verification_provenance_wiring",
    HERE / "run_runtime_version_exchange_with_verification.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RuntimeVersionExchangeProvenanceWiringTest(unittest.TestCase):
    def test_verified_runner_uses_provenance_verifier(self):
        self.assertEqual(
            "verify_runtime_version_exchange_provenance.py",
            MODULE.EVIDENCE_VERIFIER.name,
        )


if __name__ == "__main__":
    unittest.main()
