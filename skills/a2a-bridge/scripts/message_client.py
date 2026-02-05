#!/usr/bin/env python3
"""
Message Client
Handles sending and receiving A2A messages with validation and error handling.
"""

import json
import uuid
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable
import requests


class MessageType(Enum):
    """Message type enumeration."""
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    TASK_COMPLETION = "task_completion"
    PING = "ping"
    ERROR = "error"


class MessageError(Exception):
    """Base exception for message errors."""
    pass


class InvalidMessageError(MessageError):
    """Raised when message validation fails."""
    pass


class ConnectionError(MessageError):
    """Raised when connection to agent fails."""
    pass


@dataclass
class A2AMessage:
    """Represents an A2A message."""
    version: str = "1.0.0"
    message_id: str = ""
    timestamp: str = ""
    from_agent: str = ""
    to_agent: str = ""
    type: MessageType = MessageType.PING
    payload: Dict[str, Any] = None
    signature: Optional[str] = None

    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
        if self.payload is None:
            self.payload = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.type.value,
            "payload": self.payload,
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create from dictionary."""
        try:
            msg_type = MessageType(data["type"])
        except ValueError:
            raise InvalidMessageError(f"Unknown message type: {data['type']}")

        return cls(
            version=data.get("version", "1.0.0"),
            message_id=data["message_id"],
            timestamp=data["timestamp"],
            from_agent=data["from"],
            to_agent=data["to"],
            type=msg_type,
            payload=data.get("payload", {}),
            signature=data.get("signature")
        )


class MessageClient:
    """Client for sending and receiving A2A messages."""

    def __init__(self, agent_id: str, timeout: int = 30):
        """
        Initialize message client.

        Args:
            agent_id: This agent's ID
            timeout: Request timeout in seconds
        """
        self.agent_id = agent_id
        self.timeout = timeout
        self.message_handlers: Dict[MessageType, list] = {
            msg_type: [] for msg_type in MessageType
        }

    def send_message(self,
                   to_agent: str,
                   message_type: MessageType,
                   payload: Dict[str, Any],
                   endpoint: str) -> Dict[str, Any]:
        """
        Send a message to another agent.

        Args:
            to_agent: Target agent ID
            message_type: Type of message
            payload: Message payload
            endpoint: Target agent's endpoint

        Returns:
            Response from agent

        Raises:
            ConnectionError: If connection fails
            InvalidMessageError: If message is invalid
        """
        # Create message
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            type=message_type,
            payload=payload
        )

        # Validate message
        self._validate_message(message)

        # Send to endpoint
        try:
            response = requests.post(
                f"{endpoint}/a2a/messages",
                json=message.to_dict(),
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                raise InvalidMessageError(response.json().get("error", "Invalid message"))
            elif response.status_code == 404:
                raise ConnectionError(f"Agent {to_agent} not found")
            elif response.status_code == 429:
                raise ConnectionError("Rate limit exceeded")
            else:
                raise ConnectionError(f"Unexpected response: {response.status_code}")

        except requests.exceptions.Timeout:
            raise ConnectionError(f"Timeout connecting to {endpoint}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Failed to connect to {endpoint}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {e}")

    def send_task_assignment(self,
                           to_agent: str,
                           endpoint: str,
                           task_id: str,
                           task_type: str,
                           title: str,
                           description: str,
                           payload: Dict[str, Any],
                           priority: str = "medium",
                           deadline: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a task assignment message.

        Args:
            to_agent: Target agent ID
            endpoint: Target agent's endpoint
            task_id: Task ID
            task_type: Type of task
            title: Task title
            description: Task description
            payload: Task-specific payload
            priority: Task priority (low, medium, high, urgent)
            deadline: Optional deadline (ISO8601)
            metadata: Optional metadata

        Returns:
            Response from agent
        """
        task_payload = {
            "task_id": task_id,
            "task_type": task_type,
            "title": title,
            "description": description,
            "payload": payload,
            "priority": priority
        }

        if deadline:
            task_payload["deadline"] = deadline

        if metadata:
            task_payload["metadata"] = metadata

        return self.send_message(
            to_agent=to_agent,
            message_type=MessageType.TASK_ASSIGNMENT,
            payload=task_payload,
            endpoint=endpoint
        )

    def send_status_update(self,
                         to_agent: str,
                         endpoint: str,
                         task_id: str,
                         status: str,
                         progress: Optional[float] = None,
                         message: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a status update message.

        Args:
            to_agent: Target agent ID
            endpoint: Target agent's endpoint
            task_id: Task ID
            status: Task status
            progress: Optional progress (0.0-1.0)
            message: Optional status message
            metadata: Optional metadata

        Returns:
            Response from agent
        """
        status_payload = {
            "task_id": task_id,
            "status": status
        }

        if progress is not None:
            status_payload["progress"] = progress

        if message:
            status_payload["message"] = message

        if metadata:
            status_payload["metadata"] = metadata

        return self.send_message(
            to_agent=to_agent,
            message_type=MessageType.STATUS_UPDATE,
            payload=status_payload,
            endpoint=endpoint
        )

    def send_task_completion(self,
                          to_agent: str,
                          endpoint: str,
                          task_id: str,
                          result: Dict[str, Any],
                          execution_time_ms: Optional[int] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a task completion message.

        Args:
            to_agent: Target agent ID
            endpoint: Target agent's endpoint
            task_id: Task ID
            result: Task result
            execution_time_ms: Optional execution time
            metadata: Optional metadata

        Returns:
            Response from agent
        """
        completion_payload = {
            "task_id": task_id,
            "status": "completed",
            "result": result
        }

        if execution_time_ms:
            completion_payload["execution_time_ms"] = execution_time_ms

        if metadata:
            completion_payload["metadata"] = metadata

        return self.send_message(
            to_agent=to_agent,
            message_type=MessageType.TASK_COMPLETION,
            payload=completion_payload,
            endpoint=endpoint
        )

    def send_ping(self,
                 to_agent: str,
                 endpoint: str,
                 nonce: Optional[str] = None,
                 echo: Any = None) -> Dict[str, Any]:
        """
        Send a ping message.

        Args:
            to_agent: Target agent ID
            endpoint: Target agent's endpoint
            nonce: Random nonce (generated if not provided)
            echo: Optional data to echo back

        Returns:
            Response from agent
        """
        ping_payload = {
            "nonce": nonce or str(uuid.uuid4())
        }

        if echo is not None:
            ping_payload["echo"] = echo

        return self.send_message(
            to_agent=to_agent,
            message_type=MessageType.PING,
            payload=ping_payload,
            endpoint=endpoint
        )

    def on_message(self, message_type: MessageType, handler: Callable[[A2AMessage], None]):
        """
        Register a message handler.

        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type].append(handler)

    def process_message(self, message_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.

        Args:
            message_dict: Raw message dictionary

        Returns:
            Response dictionary
        """
        try:
            # Parse and validate message
            message = A2AMessage.from_dict(message_dict)
            self._validate_message(message)

            # Call handlers
            handlers = self.message_handlers.get(message.type, [])
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    # Log error but don't fail the whole process
                    print(f"Handler error: {e}")

            # Return success response
            return {
                "status": "success",
                "message_id": message.message_id,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            }

        except InvalidMessageError as e:
            return {
                "status": "error",
                "error": str(e),
                "error_code": "INVALID_MESSAGE_FORMAT"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_code": "INTERNAL_ERROR"
            }

    def _validate_message(self, message: A2AMessage):
        """
        Validate a message.

        Args:
            message: Message to validate

        Raises:
            InvalidMessageError: If message is invalid
        """
        # Check version
        if message.version != "1.0.0":
            raise InvalidMessageError(f"Unsupported version: {message.version}")

        # Check required fields
        if not message.message_id:
            raise InvalidMessageError("Missing message_id")

        if not message.timestamp:
            raise InvalidMessageError("Missing timestamp")

        if not message.from_agent:
            raise InvalidMessageError("Missing from field")

        if not message.to_agent:
            raise InvalidMessageError("Missing to field")

        if not message.type:
            raise InvalidMessageError("Missing type")

        # Validate message_id is UUID
        try:
            uuid.UUID(message.message_id)
        except ValueError:
            raise InvalidMessageError(f"Invalid message_id format: {message.message_id}")

        # Validate timestamp is ISO8601
        try:
            datetime.fromisoformat(message.timestamp.replace("Z", "+00:00"))
        except ValueError:
            raise InvalidMessageError(f"Invalid timestamp format: {message.timestamp}")

        # Validate payload based on message type
        self._validate_payload(message)

    def _validate_payload(self, message: A2AMessage):
        """
        Validate message payload based on type.

        Args:
            message: Message with payload to validate

        Raises:
            InvalidMessageError: If payload is invalid
        """
        payload = message.payload

        if not isinstance(payload, dict):
            raise InvalidMessageError("Payload must be a dictionary")

        if message.type == MessageType.TASK_ASSIGNMENT:
            required = ["task_id", "task_type", "title", "description", "payload"]
            for field in required:
                if field not in payload:
                    raise InvalidMessageError(f"Missing required field: {field}")

            # Validate priority if provided
            if "priority" in payload:
                valid_priorities = ["low", "medium", "high", "urgent"]
                if payload["priority"] not in valid_priorities:
                    raise InvalidMessageError(
                        f"Invalid priority: {payload['priority']}"
                    )

        elif message.type == MessageType.STATUS_UPDATE:
            if "task_id" not in payload:
                raise InvalidMessageError("Missing required field: task_id")

            if "status" not in payload:
                raise InvalidMessageError("Missing required field: status")

            valid_statuses = [
                "created", "assigned", "in_progress",
                "completed", "failed", "cancelled"
            ]
            if payload["status"] not in valid_statuses:
                raise InvalidMessageError(
                    f"Invalid status: {payload['status']}"
                )

        elif message.type == MessageType.TASK_COMPLETION:
            required = ["task_id", "status", "result"]
            for field in required:
                if field not in payload:
                    raise InvalidMessageError(f"Missing required field: {field}")

            if payload["status"] not in ["completed", "failed"]:
                raise InvalidMessageError(
                    f"Invalid completion status: {payload['status']}"
                )

        elif message.type == MessageType.PING:
            if "nonce" not in payload:
                raise InvalidMessageError("Missing required field: nonce")


def main():
    """CLI interface for message operations."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Message Client CLI")
    parser.add_argument("command", choices=["send", "listen"],
                       help="Command to run")
    parser.add_argument("--agent-id", help="Your agent ID")
    parser.add_argument("--target", help="Target agent ID")
    parser.add_argument("--endpoint", help="Target agent endpoint")
    parser.add_argument("--type", help="Message type")
    parser.add_argument("--payload", help="Message payload (JSON)")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Request timeout in seconds")

    args = parser.parse_args()

    if args.command == "send":
        if not args.agent_id or not args.target or not args.endpoint:
            print("Error: --agent-id, --target, and --endpoint required for send command")
            sys.exit(1)

        if not args.type:
            print("Error: --type required for send command")
            sys.exit(1)

        try:
            message_type = MessageType(args.type)
        except ValueError:
            print(f"Error: Invalid message type: {args.type}")
            sys.exit(1)

        payload = json.loads(args.payload) if args.payload else {}

        client = MessageClient(agent_id=args.agent_id, timeout=args.timeout)
        response = client.send_message(
            to_agent=args.target,
            message_type=message_type,
            payload=payload,
            endpoint=args.endpoint
        )

        print("Response:")
        print(json.dumps(response, indent=2))

    elif args.command == "listen":
        print("Listen mode not implemented in Phase 1")
        print("Use an HTTP server to receive incoming messages")
        sys.exit(1)


if __name__ == "__main__":
    main()
