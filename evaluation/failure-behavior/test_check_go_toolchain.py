#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import unittest

from check_go_toolchain import (
    controlled_environment,
    evaluate_go_version,
    parse_go_version,
    run_preflight,
)


class GoToolchainPreflightTest(unittest.TestCase):
    def test_parse_accepts_go_prefix_and_patchless_directive(self) -> None:
        self.assertEqual(parse_go_version("1.25"), (1, 25, 0))
        self.assertEqual(parse_go_version("go1.25.3"), (1, 25, 3))

    def test_equal_or_newer_toolchain_passes(self) -> None:
        self.assertEqual(evaluate_go_version("1.25", "go version go1.25.0 linux/amd64")["result"], "ok")
        self.assertEqual(evaluate_go_version("1.25", "go version go1.26.1 linux/amd64")["result"], "ok")

    def test_older_toolchain_fails(self) -> None:
        result = evaluate_go_version("1.25", "go version go1.24.9 linux/amd64")
        self.assertEqual(result["result"], "failed")
        self.assertFalse(result["automaticToolchainSwitching"])

    def test_controlled_environment_disables_ambient_go_overrides(self) -> None:
        environment = controlled_environment(
            {
                "PATH": "/bin",
                "GOTOOLCHAIN": "auto",
                "GOWORK": "/tmp/work",
                "GOENV": "/tmp/goenv",
                "GOFLAGS": "-mod=mod",
                "GOOS": "windows",
                "GOARCH": "arm64",
                "CGO_ENABLED": "1",
            }
        )
        self.assertEqual(environment["PATH"], "/bin")
        self.assertEqual(environment["GOTOOLCHAIN"], "local")
        self.assertEqual(environment["GOWORK"], "off")
        self.assertEqual(environment["GOENV"], "off")
        for key in ("GOFLAGS", "GOOS", "GOARCH", "CGO_ENABLED"):
            self.assertNotIn(key, environment)

    def test_run_preflight_fails_closed_for_old_toolchain(self) -> None:
        def runner(command, *, cwd, env, timeout):
            self.assertEqual(env["GOTOOLCHAIN"], "local")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="go version go1.24.9 linux/amd64\n",
                stderr="",
            )

        exit_code, result = run_preflight(runner=runner)
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["result"], "failed")
        self.assertEqual(result["required"], "1.25")

    def test_run_preflight_fails_closed_on_launch_error(self) -> None:
        def runner(command, *, cwd, env, timeout):
            raise OSError("go executable unavailable")

        exit_code, result = run_preflight(runner=runner)
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["result"], "failed")
        self.assertNotIn("observed", result)


if __name__ == "__main__":
    unittest.main()
