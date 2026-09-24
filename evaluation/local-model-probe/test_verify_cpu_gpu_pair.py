import copy
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).with_name("verify_cpu_gpu_pair.py")
spec = importlib.util.spec_from_file_location("pairverify", PATH)
pairverify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pairverify)


def matrix():
    pre = [{"runtime_name": "llama.cpp", "runtime_version": "b10964", "quantization": "Q4_0", "context_size": 4096, "threads": 8, "fixture": "all", "mode": mode} for mode in pairverify.MODES]
    run = {"telemetry": {"observations": [{"fixture_id": "a"}, {"fixture_id": "b"}]}}
    agg = {"total_latency_ms": 10, "first_token_latency_ms_mean": 2.0, "total_tokens": 20}
    return {"schema": pairverify.MATRIX_SCHEMA, "status": "complete", "source_git_sha": "a" * 40, "model": "qwen", "model_artifact": {"status": "observed", "sha256": "d" * 64, "size_bytes": 123}, "host": {"os": "linux", "arch": "amd64", "go_version": "go1.25.14", "logical_cpu": 8}, "preflights": pre, "raw": copy.deepcopy(run), "workspace": copy.deepcopy(run), "staged": copy.deepcopy(run), "comparison": {mode: copy.deepcopy(agg) for mode in pairverify.MODES}}


class PairTest(unittest.TestCase):
    def test_accepts_environment_only_differences(self):
        cpu, gpu = matrix(), matrix()
        gpu["host"]["logical_cpu"] = 32
        pairverify.validate_pair(cpu, gpu, 0, 99)

    def test_rejects_identity_drift(self):
        cases = [
            (lambda c, g: g.update(source_git_sha="b" * 40), "source_git_sha"),
            (lambda c, g: g["model_artifact"].update(sha256="c" * 64), "artifact"),
            (lambda c, g: g["host"].update(go_version="go1.25.15"), "host software"),
            (lambda c, g: g["preflights"][0].update(runtime_version="other"), "preflight"),
            (lambda c, g: g["workspace"]["telemetry"]["observations"].append({"fixture_id": "extra"}), "fixture set"),
        ]
        for mutate, message in cases:
            with self.subTest(message=message):
                cpu, gpu = matrix(), matrix()
                mutate(cpu, gpu)
                with self.assertRaisesRegex(ValueError, message):
                    pairverify.validate_pair(cpu, gpu, 0, 99)


if __name__ == "__main__":
    unittest.main()
