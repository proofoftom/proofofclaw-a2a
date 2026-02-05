#!/usr/bin/env python3
"""
Unit tests for Agent Card parser module.
"""

import unittest
import sys
import json
import uuid
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, '/home/node/.openclaw/workspace/skills/a2a-bridge/scripts')

from agent_card import AgentCardParser, AgentCardError, AgentCardValidationError


class TestAgentCardParser(unittest.TestCase):
    """Test AgentCardParser class."""

    def test_parse_valid_agent_card(self):
        """Test parsing a valid agent card."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["literature_review"]
        }

        result = AgentCardParser.parse(card_data)

        self.assertEqual(result["name"], "Test Agent")
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["capabilities"], ["research"])
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)

    def test_parse_json_string(self):
        """Test parsing agent card from JSON string."""
        card_json = json.dumps({
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        })

        result = AgentCardParser.parse(card_json)

        self.assertEqual(result["name"], "Test Agent")

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON string."""
        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse("invalid json {")

        self.assertIn("Invalid JSON", str(context.exception))

    def test_parse_not_dict(self):
        """Test parsing non-dictionary data."""
        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse("not a dict")

        self.assertIn("dictionary", str(context.exception))

    def test_parse_missing_required_field(self):
        """Test parsing card missing required field."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0"
            # Missing capabilities, endpoint, supported_tasks
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("Missing required fields", str(context.exception))

    def test_parse_invalid_id(self):
        """Test parsing card with invalid ID."""
        card_data = {
            "id": "not-a-uuid",
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("Invalid agent ID", str(context.exception))

    def test_parse_invalid_id_version(self):
        """Test parsing card with wrong UUID version."""
        card_data = {
            "id": str(uuid.uuid1()),  # UUID v1, not v4
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("UUID v4", str(context.exception))

    def test_parse_invalid_version(self):
        """Test parsing card with invalid version."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "invalid",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("Invalid version format", str(context.exception))

    def test_parse_empty_name(self):
        """Test parsing card with empty name."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("Name cannot be empty", str(context.exception))

    def test_parse_name_too_long(self):
        """Test parsing card with name too long."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "A" * 101,
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("exceed 100 characters", str(context.exception))

    def test_parse_empty_capabilities(self):
        """Test parsing card with empty capabilities list."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": [],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("At least one capability", str(context.exception))

    def test_parse_invalid_capability(self):
        """Test parsing card with invalid capability."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["invalid_capability"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("Unknown capability", str(context.exception))

    def test_parse_invalid_endpoint(self):
        """Test parsing card with invalid endpoint."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "not-a-url",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("valid HTTP/HTTPS URL", str(context.exception))

    def test_create_agent_card(self):
        """Test creating an agent card."""
        result = AgentCardParser.create(
            name="Test Agent",
            version="1.0.0",
            capabilities=["research"],
            endpoint="https://example.com/a2a",
            supported_tasks=["research"]
        )

        self.assertEqual(result["name"], "Test Agent")
        self.assertIn("id", result)
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)

    def test_create_generates_id(self):
        """Test that create generates an ID if not provided."""
        result = AgentCardParser.create(
            name="Test Agent",
            version="1.0.0",
            capabilities=["research"],
            endpoint="https://example.com/a2a",
            supported_tasks=["research"]
        )

        # Verify it's a valid UUID
        uuid.UUID(result["id"], version=4)

    def test_validate_capabilities_match(self):
        """Test validating capabilities match."""
        card = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research", "analysis"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        result = AgentCardParser.validate_capabilities(card, ["research"])

        self.assertTrue(result)

    def test_validate_capabilities_no_match(self):
        """Test validating capabilities when agent lacks required."""
        card = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        result = AgentCardParser.validate_capabilities(card, ["research", "analysis"])

        self.assertFalse(result)

    def test_validate_capabilities_multiple(self):
        """Test validating multiple required capabilities."""
        card = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research", "analysis", "writing"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        result = AgentCardParser.validate_capabilities(card, ["research", "analysis"])

        self.assertTrue(result)

    def test_supports_task(self):
        """Test checking if agent supports a task."""
        card = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["literature_review", "fact_checking"]
        }

        result = AgentCardParser.supports_task(card, "literature_review")

        self.assertTrue(result)

    def test_supports_task_not_found(self):
        """Test checking unsupported task."""
        card = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["literature_review"]
        }

        result = AgentCardParser.supports_task(card, "coding")

        self.assertFalse(result)

    def test_parse_with_optional_fields(self):
        """Test parsing card with optional fields."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "description": "A test agent",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"],
            "status": "busy",
            "max_concurrent_tasks": 10,
            "metadata": {"key": "value"}
        }

        result = AgentCardParser.parse(card_data)

        self.assertEqual(result["description"], "A test agent")
        self.assertEqual(result["status"], "busy")
        self.assertEqual(result["max_concurrent_tasks"], 10)
        self.assertEqual(result["metadata"]["key"], "value")

    def test_parse_with_description_too_long(self):
        """Test parsing card with description too long."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "description": "A" * 501,
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"]
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("exceed 500 characters", str(context.exception))

    def test_parse_with_invalid_status(self):
        """Test parsing card with invalid status."""
        card_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "endpoint": "https://example.com/a2a",
            "supported_tasks": ["research"],
            "status": "invalid_status"
        }

        with self.assertRaises(AgentCardValidationError) as context:
            AgentCardParser.parse(card_data)

        self.assertIn("Invalid status", str(context.exception))


if __name__ == "__main__":
    unittest.main()
