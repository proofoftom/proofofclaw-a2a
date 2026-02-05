#!/usr/bin/env python3
"""
Unit tests for Message Client module.
"""

import unittest
import sys
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, '/home/node/.openclaw/workspace/skills/a2a-bridge/scripts')

from message_client import MessageClient, A2AMessage, MessageType, InvalidMessageError, ConnectionError


class TestA2AMessage(unittest.TestCase):
    """Test A2AMessage dataclass."""

    def test_message_creation(self):
        """Test creating a message."""
        message = A2AMessage(
            from_agent="agent-001",
            to_agent="agent-002",
            type=MessageType.PING,
            payload={"nonce": "test"}
        )

        self.assertIsNotNone(message.message_id)
        self.assertIsNotNone(message.timestamp)
        self.assertEqual(message.from_agent, "agent-001")
        self.assertEqual(message.to_agent, "agent-002")
        self.assertEqual(message.type, MessageType.PING)

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        message = A2AMessage(
            from_agent="agent-001",
            to_agent="agent-002",
            type=MessageType.PING,
            payload={"nonce": "test"}
        )

        result = message.to_dict()

        self.assertEqual(result["from"], "agent-001")
        self.assertEqual(result["to"], "agent-002")
        self.assertEqual(result["type"], "ping")
        self.assertIn("message_id", result)
        self.assertIn("timestamp", result)

    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            "from": "agent-001",
            "to": "agent-002",
            "type": "ping",
            "payload": {"nonce": "test"}
        }

        message = A2AMessage.from_dict(data)

        self.assertEqual(message.from_agent, "agent-001")
        self.assertEqual(message.to_agent, "agent-002")
        self.assertEqual(message.type, MessageType.PING)
        self.assertEqual(message.payload["nonce"], "test")

    def test_message_from_dict_invalid_type(self):
        """Test creating message from dict with invalid type."""
        data = {
            "version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            "from": "agent-001",
            "to": "agent-002",
            "type": "invalid_type",
            "payload": {}
        }

        with self.assertRaises(InvalidMessageError) as context:
            A2AMessage.from_dict(data)

        self.assertIn("Unknown message type", str(context.exception))


class TestMessageClient(unittest.TestCase):
    """Test MessageClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MessageClient(agent_id="agent-001")

    def test_client_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.agent_id, "agent-001")
        self.assertEqual(self.client.timeout, 30)
        self.assertIn(MessageType.PING, self.client.message_handlers)

    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """Test sending message successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = self.client.send_message(
            to_agent="agent-002",
            message_type=MessageType.PING,
            payload={"nonce": "test"},
            endpoint="https://example.com/a2a"
        )

        self.assertEqual(result["status"], "success")

    @patch('requests.post')
    def test_send_message_timeout(self, mock_post):
        """Test sending message with timeout."""
        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(ConnectionError) as context:
            self.client.send_message(
                to_agent="agent-002",
                message_type=MessageType.PING,
                payload={"nonce": "test"},
                endpoint="https://example.com/a2a"
            )

        self.assertIn("Timeout", str(context.exception))

    @patch('requests.post')
    def test_send_message_connection_error(self, mock_post):
        """Test sending message with connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(ConnectionError) as context:
            self.client.send_message(
                to_agent="agent-002",
                message_type=MessageType.PING,
                payload={"nonce": "test"},
                endpoint="https://example.com/a2a"
            )

        self.assertIn("Failed to connect", str(context.exception))

    @patch('requests.post')
    def test_send_message_404(self, mock_post):
        """Test sending message to non-existent agent."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        with self.assertRaises(ConnectionError) as context:
            self.client.send_message(
                to_agent="agent-002",
                message_type=MessageType.PING,
                payload={"nonce": "test"},
                endpoint="https://example.com/a2a"
            )

        self.assertIn("not found", str(context.exception))

    @patch('requests.post')
    def test_send_message_400(self, mock_post):
        """Test sending invalid message."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid payload"}
        mock_post.return_value = mock_response

        with self.assertRaises(InvalidMessageError) as context:
            self.client.send_message(
                to_agent="agent-002",
                message_type=MessageType.PING,
                payload={},
                endpoint="https://example.com/a2a"
            )

        self.assertIn("Invalid message", str(context.exception))

    @patch('requests.post')
    def test_send_task_assignment(self, mock_post):
        """Test sending task assignment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = self.client.send_task_assignment(
            to_agent="agent-002",
            endpoint="https://example.com/a2a",
            task_id="task-001",
            task_type="research",
            title="Research Task",
            description="Test task",
            payload={"query": "test"}
        )

        self.assertEqual(result["status"], "success")

        # Verify payload structure
        call_args = mock_post.call_args
        sent_payload = call_args[1]["json"]["payload"]
        self.assertEqual(sent_payload["task_id"], "task-001")
        self.assertEqual(sent_payload["task_type"], "research")

    @patch('requests.post')
    def test_send_status_update(self, mock_post):
        """Test sending status update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = self.client.send_status_update(
            to_agent="agent-002",
            endpoint="https://example.com/a2a",
            task_id="task-001",
            status="in_progress",
            progress=0.5,
            message="Working on it"
        )

        self.assertEqual(result["status"], "success")

        # Verify payload structure
        call_args = mock_post.call_args
        sent_payload = call_args[1]["json"]["payload"]
        self.assertEqual(sent_payload["task_id"], "task-001")
        self.assertEqual(sent_payload["status"], "in_progress")
        self.assertEqual(sent_payload["progress"], 0.5)

    @patch('requests.post')
    def test_send_task_completion(self, mock_post):
        """Test sending task completion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = self.client.send_task_completion(
            to_agent="agent-002",
            endpoint="https://example.com/a2a",
            task_id="task-001",
            result={"summary": "Done"}
        )

        self.assertEqual(result["status"], "success")

        # Verify payload structure
        call_args = mock_post.call_args
        sent_payload = call_args[1]["json"]["payload"]
        self.assertEqual(sent_payload["task_id"], "task-001")
        self.assertEqual(sent_payload["status"], "completed")
        self.assertEqual(sent_payload["result"]["summary"], "Done")

    @patch('requests.post')
    def test_send_ping(self, mock_post):
        """Test sending ping."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "echo": {"nonce": "test"}}
        mock_post.return_value = mock_response

        result = self.client.send_ping(
            to_agent="agent-002",
            endpoint="https://example.com/a2a",
            nonce="test-nonce",
            echo={"data": "to echo"}
        )

        self.assertEqual(result["status"], "success")

    def test_on_message(self):
        """Test registering message handler."""
        handler = Mock()
        self.client.on_message(MessageType.PING, handler)

        self.assertIn(handler, self.client.message_handlers[MessageType.PING])

    def test_process_message_success(self):
        """Test processing valid message."""
        handler = Mock()
        self.client.on_message(MessageType.PING, handler)

        message_dict = {
            "version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            "from": "agent-002",
            "to": "agent-001",
            "type": "ping",
            "payload": {"nonce": "test"}
        }

        result = self.client.process_message(message_dict)

        self.assertEqual(result["status"], "success")
        handler.assert_called_once()

    def test_process_message_invalid_type(self):
        """Test processing message with invalid type."""
        message_dict = {
            "version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            "from": "agent-002",
            "to": "agent-001",
            "type": "invalid_type",
            "payload": {}
        }

        result = self.client.process_message(message_dict)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INVALID_MESSAGE_FORMAT")

    def test_process_message_missing_field(self):
        """Test processing message missing required field."""
        message_dict = {
            "version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            # Missing 'from' field
            "to": "agent-001",
            "type": "ping",
            "payload": {}
        }

        result = self.client.process_message(message_dict)

        self.assertEqual(result["status"], "error")
        self.assertIn("Missing", result["error"])

    def test_process_message_invalid_version(self):
        """Test processing message with unsupported version."""
        message_dict = {
            "version": "2.0.0",  # Unsupported
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            "from": "agent-002",
            "to": "agent-001",
            "type": "ping",
            "payload": {}
        }

        result = self.client.process_message(message_dict)

        self.assertEqual(result["status"], "error")
        self.assertIn("Unsupported version", result["error"])

    def test_validate_task_assignment_payload(self):
        """Test validating task assignment payload."""
        message = A2AMessage(
            from_agent="agent-001",
            to_agent="agent-002",
            type=MessageType.TASK_ASSIGNMENT,
            payload={"nonce": "test"}  # Missing required fields
        )

        with self.assertRaises(InvalidMessageError):
            self.client._validate_message(message)

    def test_validate_status_update_payload(self):
        """Test validating status update payload."""
        message = A2AMessage(
            from_agent="agent-001",
            to_agent="agent-002",
            type=MessageType.STATUS_UPDATE,
            payload={}  # Missing required fields
        )

        with self.assertRaises(InvalidMessageError):
            self.client._validate_message(message)

    def test_validate_task_completion_payload(self):
        """Test validating task completion payload."""
        message = A2AMessage(
            from_agent="agent-001",
            to_agent="agent-002",
            type=MessageType.TASK_COMPLETION,
            payload={}  # Missing required fields
        )

        with self.assertRaises(InvalidMessageError):
            self.client._validate_message(message)

    def test_validate_ping_payload(self):
        """Test validating ping payload."""
        message = A2AMessage(
            from_agent="agent-001",
            to_agent="agent-002",
            type=MessageType.PING,
            payload={}  # Missing required nonce
        )

        with self.assertRaises(InvalidMessageError):
            self.client._validate_message(message)

    def test_handler_exception_handling(self):
        """Test that handler exceptions don't crash processing."""
        handler = Mock(side_effect=Exception("Handler error"))
        self.client.on_message(MessageType.PING, handler)

        message_dict = {
            "version": "1.0.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": "2024-02-05T15:30:00Z",
            "from": "agent-002",
            "to": "agent-001",
            "type": "ping",
            "payload": {"nonce": "test"}
        }

        result = self.client.process_message(message_dict)

        # Should still return success despite handler error
        self.assertEqual(result["status"], "success")


if __name__ == "__main__":
    import requests
    unittest.main()
