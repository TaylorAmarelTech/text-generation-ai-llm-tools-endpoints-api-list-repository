"""
Local OpenAI-compatible proxy server.

Runs a lightweight HTTP server that accepts OpenAI API requests and
routes them through the cascade client. This lets any OpenAI-compatible
tool use your free endpoints transparently.

Usage:
    python -m tools.proxy                    # Start on port 8000
    python -m tools.proxy --port 9000        # Custom port

Then point your apps to:
    OPENAI_API_BASE=http://localhost:8000/v1
    OPENAI_API_KEY=any-string-works
"""

from __future__ import annotations

import json
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from tools.cascade import CascadeClient, DEFAULT_CASCADE


class ProxyHandler(BaseHTTPRequestHandler):
    """Handles OpenAI-compatible API requests."""

    cascade_client: CascadeClient | None = None

    def do_GET(self) -> None:
        if self.path in ("/v1/models", "/models"):
            self._handle_models()
        elif self.path in ("/health", "/"):
            self._respond(200, {"status": "ok", "message": "LLM Proxy is running"})
        else:
            self._respond(404, {"error": "Not found"})

    def do_POST(self) -> None:
        if self.path in ("/v1/chat/completions", "/chat/completions"):
            self._handle_chat()
        else:
            self._respond(404, {"error": "Not found"})

    def _handle_models(self) -> None:
        """Return a list of available models."""
        models = []
        for slot in (self.cascade_client.slots if self.cascade_client else []):
            models.append({
                "id": f"{slot.name}/{slot.model}",
                "object": "model",
                "owned_by": slot.name,
            })
        self._respond(200, {"object": "list", "data": models})

    def _handle_chat(self) -> None:
        """Handle a chat completion request via the cascade."""
        if not self.cascade_client:
            self._respond(500, {"error": "No providers configured"})
            return

        body = self._read_body()
        if not body:
            self._respond(400, {"error": "Invalid request body"})
            return

        messages = body.get("messages", [])
        if not messages:
            self._respond(400, {"error": "No messages provided"})
            return

        # Extract the last user message as prompt
        prompt = ""
        system = None
        for msg in messages:
            if msg.get("role") == "system":
                system = msg.get("content", "")
            elif msg.get("role") == "user":
                prompt = msg.get("content", "")

        max_tokens = body.get("max_tokens", 500)
        temperature = body.get("temperature", 0.7)

        try:
            start = time.time()
            response = self.cascade_client.chat(
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Return OpenAI-compatible response
            result = {
                "id": f"proxy-{int(start)}",
                "object": "chat.completion",
                "created": int(start),
                "model": response.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content,
                    },
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": response.tokens_used or 0,
                },
                "_proxy": {
                    "provider": response.provider,
                    "latency_ms": response.latency_ms,
                },
            }
            self._respond(200, result)

        except RuntimeError as e:
            self._respond(502, {"error": str(e)})

    def _read_body(self) -> dict | None:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError):
            return None

    def _respond(self, status: int, data: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        """Custom log format."""
        print(f"[proxy] {args[0]} {args[1]} {args[2]}")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Local OpenAI-compatible proxy")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    try:
        client = CascadeClient()
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Set at least one API key in .env to use the proxy.")
        sys.exit(1)

    ProxyHandler.cascade_client = client
    server = HTTPServer((args.host, args.port), ProxyHandler)

    providers_str = ", ".join(s.name for s in client.slots)
    print(f"LLM Proxy running on http://{args.host}:{args.port}")
    print(f"Providers: {providers_str}")
    print(f"\nPoint your apps to: OPENAI_BASE_URL=http://{args.host}:{args.port}/v1")
    print("Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
