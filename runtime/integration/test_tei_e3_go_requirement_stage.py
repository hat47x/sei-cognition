import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_version_exchange_evidence as subject


class TEIE3GoRequirementStageTest(unittest.TestCase):
    def make_go(
        self,
        root: Path,
        version: str,
        *,
        goos: str = "linux",
        goarch: str = "amd64",
    ) -> Path:
        path = root / version / "bin/go"
        path.parent.mkdir(parents=True)
        path.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            f"  version) echo 'go version {version} linux/amd64' ;;\n"
            "  env)\n"
            "    if [ \"$2\" = GOOS ] && [ \"$3\" = GOARCH ]; then\n"
            f"      printf '{goos}\\n{goarch}\\n'\n"
            "    else\n"
            "      exit 2\n"
            "    fi\n"
            "    ;;\n"
            "  *) exit 2 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def make_soza(self, root: Path, directive: str = "1.25") -> Path:
        go_root = root / "runtime/go"
        go_root.mkdir(parents=True)
        (go_root / "go.mod").write_text(
            f"module example.invalid/soza/runtime/go\n\ngo {directive}\n",
            encoding="utf-8",
        )
        return root

    def test_current_go_requirement_accepts_go125_linux_amd64(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza(root / "soza")
            go = self.make_go(root, "go1.25.0")
            with subject._go_on_path(go):
                observation = subject.adapter_runner._verify_soza_go_requirement(soza)
        self.assertEqual("1.25", observation["required"])
        self.assertEqual(
            "go version go1.25.0 linux/amd64",
            observation["observed"],
        )
        self.assertEqual("linux/amd64", observation["requiredTarget"])
        self.assertEqual("linux/amd64", observation["observedTarget"])

    def test_older_go_is_rejected_as_soza_go_toolchain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza(root / "soza")
            go = self.make_go(root, "go1.24.9")
            with subject._go_on_path(go):
                with self.assertRaises(
                    subject.adapter_runner.TEIAdapterStageError
                ) as raised:
                    subject.adapter_runner._verify_soza_go_requirement(soza)
        self.assertEqual("soza_go_toolchain", raised.exception.stage)
        self.assertIn("required>=1.25", raised.exception.message)

    def test_non_linux_amd64_controlled_target_is_rejected_as_soza_go_toolchain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza(root / "soza")
            go = self.make_go(root, "go1.25.0", goarch="arm64")
            with subject._go_on_path(go):
                with self.assertRaises(
                    subject.adapter_runner.TEIAdapterStageError
                ) as raised:
                    subject.adapter_runner._verify_soza_go_requirement(soza)
        self.assertEqual("soza_go_toolchain", raised.exception.stage)
        self.assertIn("linux/arm64", raised.exception.message)
        self.assertEqual(
            ["go", "env", "GOOS", "GOARCH"],
            raised.exception.command,
        )

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_combined_runner_propagates_soza_go_toolchain_failure(
        self, build, adapter
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "tei-b"
            reference = root / "tei-a"
            source.mkdir()
            reference.mkdir()
            soza = self.make_soza(root / "soza")
            tei_go = self.make_go(root, "go1.23.2")
            soza_go = self.make_go(root, "go1.24.9")
            output = root / "evidence"

            def build_success(source_repo, reference_repo, archive):
                archive.write_bytes(b"bundle")
                return {"result": "bundle_produced"}

            build.side_effect = build_success
            adapter.side_effect = subject.adapter_runner.TEIAdapterStageError(
                "soza_go_toolchain",
                "current SOZA go.modのGo要件を満たしません: required>=1.25 actual=go1.24.9",
                command=["go", "version"],
                stdout="go version go1.24.9 linux/amd64\n",
            )
            with self.assertRaises(subject.VersionExchangeRunFailed) as raised:
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )

            self.assertEqual("E3", raised.exception.stage)
            adapter.assert_called_once()
            report = json.loads(
                (output / subject.REPORT_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual("e2_verified_e3_failed", report["result"])
            self.assertEqual("E3", report["failure"]["stage"])
            self.assertEqual("soza_go_toolchain", report["failure"]["substage"])
            self.assertEqual(
                "soza_go_toolchain", report["failure"]["detail"]["stage"]
            )


if __name__ == "__main__":
    unittest.main()
