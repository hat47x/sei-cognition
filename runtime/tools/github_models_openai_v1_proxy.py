#!/usr/bin/env python3
"""E3b-M1b Evidence専用のloopback protocol shimです。

KJ Atlas固定revisionのDeepSeek transportは、OpenAI互換APIを
`/v1/chat/completions`で呼び出します。一方、GitHub Modelsの推論APIは
`/inference/chat/completions`です。本スクリプトは、このURL差だけを変換します。

モデル応答を生成・補正・固定化する機能はありません。受け取ったJSON bodyと
AuthorizationヘッダーをGitHub Modelsへ転送し、上流のstatus/bodyをそのまま
KJ Atlasへ返します。したがって、これはmodel stubではなくEvidence取得時だけの
protocol adapterです。production Provider実装やSOZAのUniversal Contractを定義しません。
"""

from __future__ import annotations

import argparse
import http.server
import urllib.error
import urllib.request

UPSTREAM_URL = "https://models.github.ai/inference/chat/completions"
MAX_BODY_BYTES = 1024 * 1024


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "soza-m1b-protocol-shim/1"

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/healthz":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok\n")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return

        authorization = self.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            self.send_error(401)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self.send_error(413)
            return

        body = self.rfile.read(content_length)
        upstream = urllib.request.Request(
            UPSTREAM_URL,
            data=body,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": authorization,
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(upstream, timeout=60) as response:
                response_body = response.read(MAX_BODY_BYTES + 1)
                if len(response_body) > MAX_BODY_BYTES:
                    self.send_error(502)
                    return
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.end_headers()
                self.wfile.write(response_body)
        except urllib.error.HTTPError as error:
            response_body = error.read(MAX_BODY_BYTES)
            self.send_response(error.code)
            self.send_header("Content-Type", error.headers.get("Content-Type", "application/json"))
            self.end_headers()
            self.wfile.write(response_body)
        except (urllib.error.URLError, TimeoutError):
            self.send_error(502)

    def log_message(self, format: str, *args: object) -> None:
        # tokenやpromptを誤ってlogへ出さないため、標準のrequest logは抑止します。
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="E3b-M1b用GitHub Models protocol shim")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("loopback以外では起動できません")

    server = http.server.ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
