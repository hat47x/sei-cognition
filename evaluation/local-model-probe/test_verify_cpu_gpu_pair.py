import copy
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).with_name("verify_cpu_gpu_pair.py")
spec = importlib.util.spec_from_file_location("pairverify", PATH)
pairverify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pairverify)


def matrix():
    pre = [
        {
            "runtime_name": "llama.cpp",
            "runtime_version": "b10964",
            "quantization": "Q4_0",
            "context_size": 4096,
            "threads": 8,
            "fixture": "all",
            "mode": mode,
        }
        for mode in pairverify.MODES
    ]
    run = {"telemetry": {"observations": [{"fixture_id": "a"}, {"fixture_id": "b"}]}}
    agg = {"total_latency_ms": 10, "first_token_latency_ms_mean": 2.0, "total_tokens": 20}
    return {
        "schema": pairverify.MATRIX_SCHEMA,
        "status": "complete",
        "source_git_sha": "a" * 40,
        "model": "qwen",
        "model_artifact": {
            "status": "observed",
            "sha256": "d" * 64,
            "size_bytes": 123,
        },
        "host": {
            "os": "linux",
            "arch": "amd64",
            "go_version": "go1.25.14",
            "logical_cpu": 8,
        },
        "preflights": pre,
        "raw": copy.deepcopy(run),
        "workspace": copy.deepcopy(run),
        "staged": copy.deepcopy(run),
        "comparison": {mode: copy.deepcopy(agg) for mode in pairverify.MODES},
    }


def cpu_offload():
    return pairverify.parse_gpu_offload_text(
        "load_tensors: offloaded 0/29 layers to GPU\n"
    )


def gpu_offload():
    return pairverify.parse_gpu_offload_text(
        "2026-09-24T00:00:00Z load_tensors: offloaded 29/29 layers to GPU\n"
        "load_tensors: CUDA0 model buffer size = 512.00 MiB\n"
    )


class PairTest(unittest.TestCase):
    def test_accepts_environment_only_differences_with_observed_gpu_offload(self):
        cpu, gpu = matrix(), matrix()
        gpu["host"]["logical_cpu"] = 32
        pairverify.validate_pair(cpu, gpu, 0, 99, cpu_offload(), gpu_offload())

    def test_parses_observed_offload_with_log_prefix(self):
        observed = gpu_offload()
        self.assertEqual(observed["status"], "observed")
        self.assertEqual(observed["offloaded_layers"], 29)
        self.assertEqual(observed["total_layers"], 29)

    def test_missing_gpu_offload_is_rejected(self):
        cpu, gpu = matrix(), matrix()
        missing = pairverify.parse_gpu_offload_text("server ready\n")
        with self.assertRaisesRegex(ValueError, "no observed layer-offload"):
            pairverify.validate_pair(cpu, gpu, 0, 99, cpu_offload(), missing)

    def test_zero_gpu_offload_is_rejected(self):
        cpu, gpu = matrix(), matrix()
        zero = pairverify.parse_gpu_offload_text(
            "load_tensors: offloaded 0/29 layers to GPU\n"
        )
        with self.assertRaisesRegex(ValueError, "did not observe positive"):
            pairverify.validate_pair(cpu, gpu, 0, 99, cpu_offload(), zero)

    def test_positive_cpu_offload_is_rejected(self):
        cpu, gpu = matrix(), matrix()
        positive_cpu = pairverify.parse_gpu_offload_text(
            "load_tensors: offloaded 1/29 layers to GPU\n"
        )
        with self.assertRaisesRegex(ValueError, "CPU run observed positive"):
            pairverify.validate_pair(cpu, gpu, 0, 99, positive_cpu, gpu_offload())

    def test_ambiguous_offload_log_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "ambiguous GPU offload"):
            pairverify.parse_gpu_offload_text(
                "load_tensors: offloaded 1/29 layers to GPU\n"
                "load_tensors: offloaded 29/29 layers to GPU\n"
            )

    def test_rejects_identity_drift(self):
        cases = [
            (lambda c, g: g.update(source_git_sha="b" * 40), "source_git_sha"),
            (lambda c, g: g["model_artifact"].update(sha256="c" * 64), "artifact"),
            (lambda c, g: g["host"].update(go_version="go1.25.15"), "host software"),
            (lambda c, g: g["preflights"][0].update(runtime_version="other"), "preflight"),
            (
                lambda c, g: g["workspace"]["telemetry"]["observations"].append(
                    {"fixture_id": "extra"}
                ),
                "fixture set",
            ),
        ]
        for mutate, message in cases:
            with self.subTest(message=message):
                cpu, gpu = matrix(), matrix()
                mutate(cpu, gpu)
                with self.assertRaisesRegex(ValueError, message):
                    pairverify.validate_pair(
                        cpu,
                        gpu,
                        0,
                        99,
                        cpu_offload(),
                        gpu_offload(),
                    )


if __name__ == "__main__":
    unittest.main()
