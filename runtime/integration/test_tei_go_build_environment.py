import os
import unittest
from unittest import mock

import run_tei_bundle_adapter_compatibility as e3
import run_tei_revision_b_prepositioned as e2


BUILD_SURFACE_OVERRIDES = (
    "GOFLAGS",
    "GOOS",
    "GOARCH",
    "GOAMD64",
    "GOEXPERIMENT",
    "CGO_ENABLED",
)


class TEIGoBuildEnvironmentTest(unittest.TestCase):
    def assert_controlled_environment(self, builder):
        parent = {
            "PATH": "/custom/bin",
            "GOPROXY": "https://proxy.example.invalid",
            "GOWORK": "/tmp/injected.work",
            "GOENV": "/tmp/injected-goenv",
            "GOTOOLCHAIN": "auto",
        }
        parent.update({key: f"injected-{key.lower()}" for key in BUILD_SURFACE_OVERRIDES})

        with mock.patch.dict(os.environ, parent, clear=True):
            environment = builder()

        self.assertEqual("off", environment["GOWORK"])
        self.assertEqual("off", environment["GOENV"])
        self.assertEqual("local", environment["GOTOOLCHAIN"])
        for key in BUILD_SURFACE_OVERRIDES:
            self.assertNotIn(key, environment)
        self.assertEqual("/custom/bin", environment["PATH"])
        self.assertEqual("https://proxy.example.invalid", environment["GOPROXY"])

    def test_e2_build_environment_ignores_ambient_build_surface_overrides(self):
        self.assert_controlled_environment(e2._controlled_go_env)

    def test_e3_test_environment_ignores_ambient_build_surface_overrides(self):
        self.assert_controlled_environment(e3._go_toolchain_env)


if __name__ == "__main__":
    unittest.main()
