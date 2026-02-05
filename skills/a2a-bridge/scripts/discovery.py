#!/usr/bin/env python3
"""
Agent Discovery Module
Handles local agent discovery and registration.
"""

import json
import socket
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import requests
from urllib.parse import urlparse


@dataclass
class AgentInfo:
    """Represents discovered agent information."""
    id: str
    name: str
    version: str
    endpoint: str
    capabilities: List[str]
    supported_tasks: List[str]
    status: str = "active"
    metadata: Dict[str, Any] = None
    last_seen: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.last_seen == 0.0:
            self.last_seen = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "supported_tasks": self.supported_tasks,
            "status": self.status,
            "metadata": self.metadata,
            "last_seen": self.last_seen
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInfo":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            endpoint=data["endpoint"],
            capabilities=data.get("capabilities", []),
            supported_tasks=data.get("supported_tasks", []),
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
            last_seen=data.get("last_seen", time.time())
        )


class AgentDiscovery:
    """Agent discovery service."""

    def __init__(self, discovery_port: int = 8765, timeout: int = 5):
        """
        Initialize discovery service.

        Args:
            discovery_port: Port for discovery broadcasts
            timeout: Request timeout in seconds
        """
        self.discovery_port = discovery_port
        self.timeout = timeout
        self.known_agents: Dict[str, AgentInfo] = {}

    def discover_local(self, scan_ports: List[int] = None) -> List[AgentInfo]:
        """
        Discover agents on local network.

        Args:
            scan_ports: List of ports to scan (default: [8765, 8766, 8767])

        Returns:
            List of discovered agents
        """
        if scan_ports is None:
            scan_ports = [8765, 8766, 8767]

        discovered = []

        # Scan common localhost ports
        for port in scan_ports:
            try:
                agent_card = self._fetch_agent_card("localhost", port)
                if agent_card:
                    agent_info = AgentInfo(
                        id=agent_card["id"],
                        name=agent_card["name"],
                        version=agent_card["version"],
                        endpoint=agent_card["endpoint"],
                        capabilities=agent_card.get("capabilities", []),
                        supported_tasks=agent_card.get("supported_tasks", []),
                        status=agent_card.get("status", "active"),
                        metadata=agent_card.get("metadata", {})
                    )
                    discovered.append(agent_info)
                    self.known_agents[agent_info.id] = agent_info
            except Exception as e:
                # Silently skip non-responsive ports
                pass

        return discovered

    def discover_from_url(self, url: str) -> Optional[AgentInfo]:
        """
        Discover agent from specific URL.

        Args:
            url: Agent endpoint URL (e.g., https://agent.example.com)

        Returns:
            AgentInfo if found, None otherwise
        """
        try:
            # Try common agent card endpoints
            card_urls = [
                f"{url}/agent-card.json",
                f"{url}/.well-known/agent-card.json",
                f"{url}/a2a/agent-card"
            ]

            for card_url in card_urls:
                response = requests.get(card_url, timeout=self.timeout)
                if response.status_code == 200:
                    agent_card = response.json()
                    agent_info = AgentInfo.from_dict(agent_card)
                    self.known_agents[agent_info.id] = agent_info
                    return agent_info

        except Exception as e:
            return None

        return None

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """
        Get information about a specific agent.

        Args:
            agent_id: Agent UUID

        Returns:
            AgentInfo if found, None otherwise
        """
        return self.known_agents.get(agent_id)

    def register_self(self, agent_card: Dict[str, Any]) -> bool:
        """
        Register current agent as discoverable (for Phase 2).

        Args:
            agent_card: Agent Card dictionary

        Returns:
            True if registration successful
        """
        # Placeholder for Phase 1 - registration will be implemented
        # with discovery service in later phases
        print("Self-registration not implemented in Phase 1")
        return False

    def find_by_capability(self, capability: str) -> List[AgentInfo]:
        """
        Find agents with a specific capability.

        Args:
            capability: Required capability

        Returns:
            List of agents with the capability
        """
        return [
            agent for agent in self.known_agents.values()
            if capability in agent.capabilities
        ]

    def find_by_task(self, task_type: str) -> List[AgentInfo]:
        """
        Find agents that support a specific task type.

        Args:
            task_type: Task type to match

        Returns:
            List of agents that support the task
        """
        return [
            agent for agent in self.known_agents.values()
            if task_type in agent.supported_tasks
        ]

    def find_by_capabilities(self, capabilities: List[str]) -> List[AgentInfo]:
        """
        Find agents that have all required capabilities.

        Args:
            capabilities: List of required capabilities

        Returns:
            List of agents with all required capabilities
        """
        return [
            agent for agent in self.known_agents.values()
            if all(cap in agent.capabilities for cap in capabilities)
        ]

    def _fetch_agent_card(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Fetch agent card from a host/port.

        Args:
            host: Hostname or IP
            port: Port number

        Returns:
            Agent card dictionary or None
        """
        try:
            # Try multiple endpoints
            endpoints = [
                f"http://{host}:{port}/agent-card.json",
                f"http://{host}:{port}/a2a/agent-card"
            ]

            for endpoint in endpoints:
                response = requests.get(endpoint, timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()

        except Exception:
            return None

        return None

    def refresh_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """
        Refresh agent information by re-fetching its card.

        Args:
            agent_id: Agent UUID to refresh

        Returns:
            Updated AgentInfo or None if not found
        """
        agent = self.known_agents.get(agent_id)
        if not agent:
            return None

        # Parse endpoint URL
        parsed = urlparse(agent.endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or 80

        updated_card = self._fetch_agent_card(host, port)
        if updated_card:
            updated_agent = AgentInfo.from_dict(updated_card)
            self.known_agents[agent_id] = updated_agent
            return updated_agent

        return None

    def cleanup_stale_agents(self, max_age_seconds: int = 3600) -> int:
        """
        Remove agents that haven't been seen recently.

        Args:
            max_age_seconds: Maximum age in seconds

        Returns:
            Number of agents removed
        """
        current_time = time.time()
        stale_ids = []

        for agent_id, agent in self.known_agents.items():
            age = current_time - agent.last_seen
            if age > max_age_seconds:
                stale_ids.append(agent_id)

        for agent_id in stale_ids:
            del self.known_agents[agent_id]

        return len(stale_ids)


def main():
    """CLI interface for agent discovery."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Discovery CLI")
    parser.add_argument("command", choices=["scan", "fetch", "list"],
                       help="Command to run")
    parser.add_argument("--url", help="URL to fetch agent card from")
    parser.add_argument("--capability", help="Filter by capability")
    parser.add_argument("--task", help="Filter by task type")

    args = parser.parse_args()

    discovery = AgentDiscovery()

    if args.command == "scan":
        agents = discovery.discover_local()
        print(f"Discovered {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent.name} ({agent.id})")
            print(f"    Capabilities: {', '.join(agent.capabilities)}")
            print(f"    Tasks: {', '.join(agent.supported_tasks[:3])}...")

    elif args.command == "fetch":
        if not args.url:
            print("Error: --url required for fetch command")
            return

        agent = discovery.discover_from_url(args.url)
        if agent:
            print(f"Found agent: {agent.name} ({agent.id})")
            print(f"Endpoint: {agent.endpoint}")
            print(f"Capabilities: {', '.join(agent.capabilities)}")
            print(f"Tasks: {', '.join(agent.supported_tasks)}")
        else:
            print(f"No agent found at {args.url}")

    elif args.command == "list":
        agents = list(discovery.known_agents.values())

        if args.capability:
            agents = discovery.find_by_capability(args.capability)
            print(f"Agents with capability '{args.capability}':")
        elif args.task:
            agents = discovery.find_by_task(args.task)
            print(f"Agents supporting task '{args.task}':")
        else:
            print(f"Known agents ({len(agents)}):")

        for agent in agents:
            print(f"  - {agent.name} ({agent.id})")
            print(f"    Status: {agent.status}")


if __name__ == "__main__":
    main()
