#!/usr/bin/env python3
"""
Unit tests for Agent Discovery module.
"""

import unittest
import sys
from unittest.mock import patch, Mock
import time

# Add scripts directory to path
sys.path.insert(0, '/home/node/.openclaw/workspace/skills/a2a-bridge/scripts')

from discovery import AgentDiscovery, AgentInfo


class TestAgentInfo(unittest.TestCase):
    """Test AgentInfo dataclass."""

    def test_creation(self):
        """Test creating AgentInfo."""
        agent = AgentInfo(
            id="agent-001",
            name="Test Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["literature_review"]
        )

        self.assertEqual(agent.id, "agent-001")
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.status, "active")
        self.assertIsInstance(agent.metadata, dict)
        self.assertGreater(agent.last_seen, 0)

    def test_to_dict(self):
        """Test converting AgentInfo to dictionary."""
        agent = AgentInfo(
            id="agent-001",
            name="Test Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["literature_review"]
        )

        result = agent.to_dict()

        self.assertEqual(result["id"], "agent-001")
        self.assertEqual(result["name"], "Test Agent")
        self.assertIn("capabilities", result)
        self.assertIn("supported_tasks", result)

    def test_from_dict(self):
        """Test creating AgentInfo from dictionary."""
        data = {
            "id": "agent-001",
            "name": "Test Agent",
            "version": "1.0.0",
            "endpoint": "https://example.com/a2a",
            "capabilities": ["research"],
            "supported_tasks": ["literature_review"],
            "status": "busy"
        }

        agent = AgentInfo.from_dict(data)

        self.assertEqual(agent.id, "agent-001")
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.status, "busy")


class TestAgentDiscovery(unittest.TestCase):
    """Test AgentDiscovery class."""

    def setUp(self):
        """Set up test fixtures."""
        self.discovery = AgentDiscovery()

    def test_initialization(self):
        """Test discovery initialization."""
        self.assertEqual(self.discovery.discovery_port, 8765)
        self.assertEqual(self.discovery.timeout, 5)
        self.assertIsInstance(self.discovery.known_agents, dict)

    def test_find_by_capability(self):
        """Test finding agents by capability."""
        agent1 = AgentInfo(
            id="agent-001",
            name="Research Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research", "analysis"],
            supported_tasks=["literature_review"]
        )

        agent2 = AgentInfo(
            id="agent-002",
            name="Coding Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["coding"],
            supported_tasks=["implementation"]
        )

        self.discovery.known_agents["agent-001"] = agent1
        self.discovery.known_agents["agent-002"] = agent2

        results = self.discovery.find_by_capability("research")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "agent-001")

    def test_find_by_task(self):
        """Test finding agents by task type."""
        agent1 = AgentInfo(
            id="agent-001",
            name="Research Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["literature_review", "fact_checking"]
        )

        agent2 = AgentInfo(
            id="agent-002",
            name="Coding Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["coding"],
            supported_tasks=["implementation"]
        )

        self.discovery.known_agents["agent-001"] = agent1
        self.discovery.known_agents["agent-002"] = agent2

        results = self.discovery.find_by_task("literature_review")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "agent-001")

    def test_find_by_capabilities(self):
        """Test finding agents with all required capabilities."""
        agent1 = AgentInfo(
            id="agent-001",
            name="Multi-Skilled Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research", "analysis", "writing"],
            supported_tasks=["research"]
        )

        agent2 = AgentInfo(
            id="agent-002",
            name="Research Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["research"]
        )

        self.discovery.known_agents["agent-001"] = agent1
        self.discovery.known_agents["agent-002"] = agent2

        results = self.discovery.find_by_capabilities(["research", "analysis"])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "agent-001")

    def test_get_agent_info(self):
        """Test getting agent info by ID."""
        agent = AgentInfo(
            id="agent-001",
            name="Test Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["research"]
        )

        self.discovery.known_agents["agent-001"] = agent

        result = self.discovery.get_agent_info("agent-001")

        self.assertIsNotNone(result)
        self.assertEqual(result.id, "agent-001")

    def test_get_agent_info_not_found(self):
        """Test getting non-existent agent."""
        result = self.discovery.get_agent_info("agent-999")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_discover_from_url(self, mock_get):
        """Test discovering agent from URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "agent-001",
            "name": "Test Agent",
            "version": "1.0.0",
            "capabilities": ["research"],
            "supported_tasks": ["research"],
            "endpoint": "https://example.com/a2a"
        }
        mock_get.return_value = mock_response

        result = self.discovery.discover_from_url("https://example.com")

        self.assertIsNotNone(result)
        self.assertEqual(result.id, "agent-001")
        self.assertEqual(result.name, "Test Agent")

    @patch('requests.get')
    def test_discover_from_url_not_found(self, mock_get):
        """Test discovering agent from URL when not found."""
        mock_get.return_value = Mock(status_code=404)

        result = self.discovery.discover_from_url("https://example.com")

        self.assertIsNone(result)

    def test_cleanup_stale_agents(self):
        """Test cleaning up stale agents."""
        # Add an old agent
        old_agent = AgentInfo(
            id="agent-001",
            name="Old Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["research"]
        )
        old_agent.last_seen = time.time() - 7200  # 2 hours ago

        # Add a recent agent
        recent_agent = AgentInfo(
            id="agent-002",
            name="Recent Agent",
            version="1.0.0",
            endpoint="https://example.com/a2a",
            capabilities=["research"],
            supported_tasks=["research"]
        )
        recent_agent.last_seen = time.time() - 600  # 10 minutes ago

        self.discovery.known_agents["agent-001"] = old_agent
        self.discovery.known_agents["agent-002"] = recent_agent

        removed = self.discovery.cleanup_stale_agents(max_age_seconds=3600)

        self.assertEqual(removed, 1)
        self.assertNotIn("agent-001", self.discovery.known_agents)
        self.assertIn("agent-002", self.discovery.known_agents)


if __name__ == "__main__":
    unittest.main()
