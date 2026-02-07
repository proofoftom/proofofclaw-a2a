#!/usr/bin/env python3
"""
Simple HTTP server for serving Agent A Card
"""

import json
import socket

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

def handle_request(client_socket, client_address):
    """Handle HTTP request from client socket."""
    try:
        request_data = client_socket.recv(4096).decode('utf-8')
        print(f"[Server] Received from {client_address}: {request_data[:100]}")
        
        if request_data.startswith('GET /agent-card.json'):
            # Prepare JSON response
            response_body = json.dumps(agent_a_card, indent=2)
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"{response_body}"
            )
            client_socket.send(response.encode('utf-8'))
            print(f"[Server] Sent Agent Card to {client_address}")
        else:
            response = (
                f"HTTP/1.1 404 Not Found\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: 9\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"Not found"
            )
            client_socket.send(response.encode('utf-8'))
            print(f"[Server] 404 for {client_address}")
    except Exception as e:
        print(f"[Server] Error handling {client_address}: {e}")
    finally:
        client_socket.close()

def run_server():
    """Run the HTTP server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 8765))
    server_socket.listen(5)
    
    print("[Server] Starting discovery server on port 8765")
    print("[Server] Serving Agent Card at http://0.0.0.0:8765/agent-card.json")
    print("[Server] Press Ctrl+C to stop")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"[Server] Connection from {client_address}")
            handle_request(client_socket, client_address)
    except KeyboardInterrupt:
        print("\n[Server] Server stopped")
        server_socket.close()

if __name__ == "__main__":
    run_server()
