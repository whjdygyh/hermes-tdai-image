"""
Feishu / Lark Webhook Receiver — Standalone HTTP Server

Minimal Python webhook server that handles Feishu event subscription callbacks.
Use when Hermes' built-in webhook adapter can't be used (e.g., gateway not running).

Usage:
  python3 feishu-webhook-receiver.py <port>

Feishu will POST events to the public URL. The server:
  1. Responds to challenge verification ({"challenge": "..."})
  2. Logs all received events to /tmp/feishu_webhooks.log
  3. Returns 200 OK for all valid requests
"""

import http.server
import json
import sys
import os


class FeishuWebhookHandler(http.server.BaseHTTPRequestHandler):
    """Handles Feishu event subscription callbacks."""

    LOG_PATH = "/tmp/feishu_webhooks.log"

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Log the raw event
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)
        with open(self.LOG_PATH, "a") as f:
            f.write(f"[{self.path}] {body.decode('utf-8', errors='replace')}\n---\n")

        # Handle Feishu URL verification challenge
        try:
            data = json.loads(body)
            if "challenge" in data:
                self._respond_json({"challenge": data["challenge"]})
                print(f"✅ Challenge verified: {data['challenge'][:20]}...", flush=True)
                return
            print(f"📩 Event received: {self.path} — {body[:200]}", flush=True)
        except json.JSONDecodeError:
            pass

        self._respond_json({"code": 0})

    def do_GET(self):
        """Health check endpoint."""
        self._respond_text("Feishu Webhook Receiver Ready")

    def _respond_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _respond_text(self, text: str, status: int = 200):
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Suppress default HTTP server logs."""
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8644
    server = http.server.HTTPServer(("0.0.0.0", port), FeishuWebhookHandler)
    print(f"🚀 Feishu webhook receiver listening on port {port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")
        server.server_close()
