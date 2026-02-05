#!/usr/bin/env python3
"""
Agent Card Parser
Handles parsing, validation, and creation of Agent Cards.
"""

import json
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


class AgentCardError(Exception):
    """Base exception for Agent Card errors."""
    pass


class AgentCardValidationError(AgentCardError):
    """Raised when Agent Card validation fails."""
    pass


class AgentCardParser:
    """Parser and validator for Agent Cards."""

    # Built-in capabilities
    BUILT_IN_CAPABILITIES = [
        "research",
        "analysis",
        "coding",
        "writing",
        "planning",
        "monitoring",
        "testing",
        "deployment",
        "custom"
    ]

    # Valid status values
    VALID_STATUSES = ["active", "inactive", "busy", "offline"]

    # Valid priorities
    VALID_PRIORITIES = ["low", "medium", "high", "urgent"]

    @staticmethod
    def parse(data: Any) -> Dict[str, Any]:
        """
        Parse and validate an Agent Card.

        Args:
            data: Agent card data (dict or JSON string)

        Returns:
            Validated agent card dictionary

        Raises:
            AgentCardValidationError: If validation fails
        """
        # Parse JSON string if needed
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise AgentCardValidationError(f"Invalid JSON: {e}")

        # Ensure it's a dictionary
        if not isinstance(data, dict):
            raise AgentCardValidationError("Agent Card must be a dictionary")

        # Validate required fields
        AgentCardParser._validate_required_fields(data)

        # Validate individual fields
        AgentCardParser._validate_id(data["id"])
        AgentCardParser._validate_name(data["name"])
        AgentCardParser._validate_version(data["version"])
        AgentCardParser._validate_capabilities(data["capabilities"])
        AgentCardParser._validate_endpoint(data["endpoint"])
        AgentCardParser._validate_supported_tasks(data["supported_tasks"])

        # Validate optional fields
        if "description" in data:
            AgentCardParser._validate_description(data["description"])

        if "status" in data:
            AgentCardParser._validate_status(data["status"])

        if "max_concurrent_tasks" in data:
            AgentCardParser._validate_max_concurrent_tasks(data["max_concurrent_tasks"])

        if "rate_limit" in data:
            AgentCardParser._validate_rate_limit(data["rate_limit"])

        # Add timestamps if missing
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow().isoformat() + "Z"

        data["updated_at"] = datetime.utcnow().isoformat() + "Z"

        return data

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """
        Create a new Agent Card from fields.

        Args:
            **kwargs: Agent card fields

        Returns:
            Validated agent card dictionary

        Raises:
            AgentCardValidationError: If validation fails
        """
        # Generate ID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())

        # Validate using parse
        return AgentCardParser.parse(kwargs)

    @staticmethod
    def validate_capabilities(agent_card: Dict[str, Any],
                             required: List[str]) -> bool:
        """
        Check if agent has all required capabilities.

        Args:
            agent_card: Validated agent card
            required: List of required capabilities

        Returns:
            True if agent has all required capabilities
        """
        agent_capabilities = set(agent_card.get("capabilities", []))
        required_capabilities = set(required)

        return required_capabilities.issubset(agent_capabilities)

    @staticmethod
    def supports_task(agent_card: Dict[str, Any],
                     task_type: str) -> bool:
        """
        Check if agent supports a specific task type.

        Args:
            agent_card: Validated agent card
            task_type: Task type to check

        Returns:
            True if agent supports the task
        """
        supported_tasks = agent_card.get("supported_tasks", [])
        return task_type in supported_tasks

    @staticmethod
    def _validate_required_fields(data: Dict[str, Any]):
        """Validate that all required fields are present."""
        required_fields = [
            "id", "name", "version",
            "capabilities", "endpoint", "supported_tasks"
        ]

        missing = [field for field in required_fields if field not in data]
        if missing:
            raise AgentCardValidationError(
                f"Missing required fields: {', '.join(missing)}"
            )

    @staticmethod
    def _validate_id(agent_id: str):
        """Validate agent ID (must be UUID v4)."""
        try:
            parsed = uuid.UUID(agent_id)
            # Check version is 4
            if parsed.version != 4:
                raise AgentCardValidationError(
                    "Agent ID must be UUID v4"
                )
        except ValueError:
            raise AgentCardValidationError(
                f"Invalid agent ID: {agent_id}"
            )

    @staticmethod
    def _validate_name(name: str):
        """Validate agent name."""
        if not isinstance(name, str):
            raise AgentCardValidationError("Name must be a string")

        if len(name) == 0:
            raise AgentCardValidationError("Name cannot be empty")

        if len(name) > 100:
            raise AgentCardValidationError(
                "Name cannot exceed 100 characters"
            )

    @staticmethod
    def _validate_version(version: str):
        """Validate semantic versioning."""
        if not isinstance(version, str):
            raise AgentCardValidationError("Version must be a string")

        # Semantic versioning pattern: MAJOR.MINOR.PATCH
        pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(pattern, version):
            raise AgentCardValidationError(
                f"Invalid version format: {version}. "
                "Expected semantic versioning (e.g., 1.0.0)"
            )

    @staticmethod
    def _validate_capabilities(capabilities: List[str]):
        """Validate capabilities list."""
        if not isinstance(capabilities, list):
            raise AgentCardValidationError("Capabilities must be a list")

        if len(capabilities) == 0:
            raise AgentCardValidationError(
                "At least one capability is required"
            )

        for cap in capabilities:
            if not isinstance(cap, str):
                raise AgentCardValidationError(
                    "All capabilities must be strings"
                )

            if cap not in AgentCardParser.BUILT_IN_CAPABILITIES:
                raise AgentCardValidationError(
                    f"Unknown capability: {cap}. "
                    f"Valid capabilities: {', '.join(AgentCardParser.BUILT_IN_CAPABILITIES)}"
                )

    @staticmethod
    def _validate_endpoint(endpoint: str):
        """Validate endpoint URL."""
        if not isinstance(endpoint, str):
            raise AgentCardValidationError("Endpoint must be a string")

        # Basic URL validation
        if not endpoint.startswith(("http://", "https://")):
            raise AgentCardValidationError(
                "Endpoint must be a valid HTTP/HTTPS URL"
            )

    @staticmethod
    def _validate_supported_tasks(tasks: List[str]):
        """Validate supported tasks list."""
        if not isinstance(tasks, list):
            raise AgentCardValidationError("Supported tasks must be a list")

        if len(tasks) == 0:
            raise AgentCardValidationError(
                "At least one supported task is required"
            )

        for task in tasks:
            if not isinstance(task, str):
                raise AgentCardValidationError(
                    "All supported tasks must be strings"
                )

            if len(task) == 0:
                raise AgentCardValidationError(
                    "Task type cannot be empty"
                )

            if len(task) > 50:
                raise AgentCardValidationError(
                    f"Task type '{task}' exceeds 50 characters"
                )

    @staticmethod
    def _validate_description(description: str):
        """Validate description."""
        if not isinstance(description, str):
            raise AgentCardValidationError("Description must be a string")

        if len(description) > 500:
            raise AgentCardValidationError(
                "Description cannot exceed 500 characters"
            )

    @staticmethod
    def _validate_status(status: str):
        """Validate status."""
        if status not in AgentCardParser.VALID_STATUSES:
            raise AgentCardValidationError(
                f"Invalid status: {status}. "
                f"Valid statuses: {', '.join(AgentCardParser.VALID_STATUSES)}"
            )

    @staticmethod
    def _validate_max_concurrent_tasks(max_tasks: int):
        """Validate max concurrent tasks."""
        if not isinstance(max_tasks, int):
            raise AgentCardValidationError(
                "max_concurrent_tasks must be an integer"
            )

        if max_tasks < 1:
            raise AgentCardValidationError(
                "max_concurrent_tasks must be >= 1"
            )

    @staticmethod
    def _validate_rate_limit(rate_limit: Dict[str, Any]):
        """Validate rate limit configuration."""
        if not isinstance(rate_limit, dict):
            raise AgentCardValidationError("rate_limit must be a dictionary")

        if "requests_per_minute" in rate_limit:
            rpm = rate_limit["requests_per_minute"]
            if not isinstance(rpm, int) or rpm < 1:
                raise AgentCardValidationError(
                    "rate_limit.requests_per_minute must be >= 1"
                )

        if "requests_per_hour" in rate_limit:
            rph = rate_limit["requests_per_hour"]
            if not isinstance(rph, int) or rph < 1:
                raise AgentCardValidationError(
                    "rate_limit.requests_per_hour must be >= 1"
                )


def main():
    """CLI interface for Agent Card operations."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Agent Card CLI")
    parser.add_argument("command", choices=["validate", "create"],
                       help="Command to run")
    parser.add_argument("--file", help="Path to agent card file")
    parser.add_argument("--id", help="Agent ID")
    parser.add_argument("--name", help="Agent name")
    parser.add_argument("--version", default="1.0.0", help="Agent version")
    parser.add_argument("--endpoint", help="Agent endpoint URL")
    parser.add_argument("--capabilities", nargs="+",
                       help="List of capabilities")
    parser.add_argument("--tasks", nargs="+",
                       help="List of supported tasks")

    args = parser.parse_args()

    if args.command == "validate":
        if not args.file:
            print("Error: --file required for validate command")
            sys.exit(1)

        try:
            with open(args.file, "r") as f:
                data = json.load(f)

            card = AgentCardParser.parse(data)
            print("✓ Agent Card is valid")
            print(f"  Name: {card['name']}")
            print(f"  ID: {card['id']}")
            print(f"  Version: {card['version']}")
            print(f"  Capabilities: {', '.join(card['capabilities'])}")
            print(f"  Tasks: {', '.join(card['supported_tasks'])}")

        except AgentCardValidationError as e:
            print(f"✗ Validation failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)

    elif args.command == "create":
        if not args.name or not args.endpoint:
            print("Error: --name and --endpoint required for create command")
            sys.exit(1)

        if not args.capabilities:
            args.capabilities = ["custom"]

        if not args.tasks:
            args.tasks = ["custom_task"]

        card_data = {
            "name": args.name,
            "endpoint": args.endpoint,
            "capabilities": args.capabilities,
            "supported_tasks": args.tasks
        }

        if args.id:
            card_data["id"] = args.id

        card_data["version"] = args.version

        try:
            card = AgentCardParser.create(**card_data)
            print(json.dumps(card, indent=2))

        except AgentCardValidationError as e:
            print(f"✗ Creation failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
