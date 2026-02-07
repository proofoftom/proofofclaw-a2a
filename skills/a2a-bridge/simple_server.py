#!/usr/bin/env python3
"""
Simple HTTP server for serving Agent A Card
"""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Agent Card for Agent A
agent_a_card = {
    "id": "agent-a-demo",
    "name": "Agent A (Discovery)",
    "version": "1.0.0",
    "status": "available",
    "capabilities": ["discovery", "task_execution"],
    "endpoint": "http://localhost:8765",
    "supported_tasks": ["research", "coding", "writing"]
}

class AgentCardHandler(SimpleHTTPRequestHandler):
    """Handler for serving Agent Card."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/agent-card.json":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            content = json.dumps(agent_a_card).encode('utf-8')
            self.wfile.write(content)
            print(f"[Server] Served Agent Card to {self.client_address}")
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')
            print(f"[Server] 404: {self.path}")

class ReusableHTTPServer(HTTPServer):
    """HTTPServer with address reuse enabled."""
    allow_reuse_address = True

def run_server():
    """Run the HTTP server."""
    print("[Server] Starting discovery server on port 8765")
    print("[Server] Serving Agent Card at http://localhost:8765/agent-card.json")
    print("[Server] Press Ctrl+C to stop")

    server = ReusableHTTPServer(('', 8765), AgentCardHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Server stopped")

if __name__ == "__main__":
    run_server()
