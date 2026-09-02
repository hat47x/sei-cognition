#!/usr/bin/env python3
"""E3b-M1b専用の薄いOllama接続Adapter。

KJ Atlasの既存local LLM境界（POST /generate）をOllamaのactual model inferenceへ
変換するためだけに使う。SOZAのUniversal Contractや正式なProvider protocolではない。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

MAX_BODY_BYTES = 1024 * 1024


def _write_evidence(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


class AdapterHandler(BaseHTTPRequestHandler):
    server_version = "soza-e3b-m1b-adapter/1"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        print(f"[e3b-m1b-adapter] {self.address_string()} - {format % args}")

    def _json_response(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/":
            self._json_response(404, {"error": "not_found"})
            return
        self._json_response(
            200,
            {
                "status": "ready",
                "model": self.server.model_name,
                "role": "e3b-m1b-integration-adapter",
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/generate":
            self._json_response(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_response(400, {"error": "invalid_content_length"})
            return
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self._json_response(413, {"error": "invalid_request_size"})
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json_response(400, {"error": "invalid_json"})
            return

        task = payload.get("task")
        prompt = payload.get("prompt")
        requested_model = payload.get("model")
        temperature = payload.get("temperature", 0.2)
        max_tokens = payload.get("max_tokens", 2000)

        if not isinstance(task, str) or not task:
            self._json_response(400, {"error": "invalid_task"})
            return
        if not isinstance(prompt, str) or not prompt:
            self._json_response(400, {"error": "invalid_prompt"})
            return
        if requested_model not in (None, self.server.model_name):
            self._json_response(
                409,
                {
                    "error": "model_mismatch",
                    "requested": requested_model,
                    "configured": self.server.model_name,
                },
            )
            return
        if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
            self._json_response(400, {"error": "invalid_temperature"})
            return
        if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens < 1:
            self._json_response(400, {"error": "invalid_max_tokens"})
            return

        # `format: json`はOllamaのJSON modeを使うためのtransport-local設定であり、
        # KJ Atlasのprompt本文は変更しない。意味内容はactual modelが生成する。
        ollama_payload = {
            "model": self.server.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": float(temperature),
                "num_predict": min(max_tokens, 2048),
            },
        }
        ollama_request = request.Request(
            f"{self.server.ollama_base_url.rstrip('/')}/api/generate",
            data=json.dumps(ollama_payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(ollama_request, timeout=180) as response:
                model_response = json.loads(response.read(MAX_BODY_BYTES).decode("utf-8"))
        except (error.URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json_response(502, {"error": "ollama_request_failed", "detail": str(exc)})
            return

        generated = model_response.get("response")
        if not isinstance(generated, str) or not generated.strip():
            self._json_response(502, {"error": "ollama_response_missing_text"})
            return
        try:
            json.loads(generated)
        except json.JSONDecodeError:
            self._json_response(502, {"error": "ollama_response_not_json"})
            return

        evidence = {
            "schema": "soza.e3b-m1b-model-call/v1",
            "adapter_role": "integration-only",
            "task": task,
            "model": self.server.model_name,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "ollama_done": model_response.get("done"),
            "ollama_done_reason": model_response.get("done_reason"),
            "prompt_eval_count": model_response.get("prompt_eval_count"),
            "eval_count": model_response.get("eval_count"),
            "total_duration": model_response.get("total_duration"),
            "load_duration": model_response.get("load_duration"),
        }
        _write_evidence(self.server.evidence_path, evidence)
        self._json_response(200, {"text": generated})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument(
        "--ollama-base-url",
        default=os.environ.get("SOZA_M1B_OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("SOZA_M1B_MODEL", "qwen2.5:0.5b"),
    )
    parser.add_argument(
        "--evidence",
        default=os.environ.get(
            "SOZA_M1B_MODEL_EVIDENCE", "/tmp/soza-e3b-m1b-model-call.json"
        ),
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), AdapterHandler)
    server.ollama_base_url = args.ollama_base_url
    server.model_name = args.model
    server.evidence_path = Path(args.evidence)
    print(
        f"E3b-M1b adapter ready: http://{args.host}:{args.port} -> "
        f"{args.ollama_base_url} model={args.model}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
