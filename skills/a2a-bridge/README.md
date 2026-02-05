# A2A Bridge Skill

Agent-to-Agent (A2A) protocol implementation for inter-agent communication, task delegation, and collaboration.

## Overview

This skill enables AI agents to:
- Discover and communicate with other agents
- Parse and validate Agent Cards for capability matching
- Manage task lifecycle (assign, update, complete)
- Send/receive A2A messages with proper validation

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python scripts/discovery.py scan
python scripts/agent_card.py validate examples/agent-card.json
python scripts/task_lifecycle.py list
```

## Quick Start

### Agent Discovery

```python
from scripts.discovery import AgentDiscovery

discovery = AgentDiscovery()
agents = discovery.discover_local()

for agent in agents:
    print(f"Found: {agent.name} ({agent.id})")
    print(f"  Capabilities: {', '.join(agent.capabilities)}")
```

### Agent Card Parsing

```python
from scripts.agent_card import AgentCardParser

card = AgentCardParser.parse({
    "id": "agent-uuid",
    "name": "Research Agent",
    "version": "1.0.0",
    "capabilities": ["research"],
    "endpoint": "https://agent.example.com/a2a",
    "supported_tasks": ["literature_review"]
})

if AgentCardParser.validate_capabilities(card, ["research"]):
    print("Agent can handle research tasks")
```

### Task Management

```python
from scripts.task_lifecycle import TaskManager

manager = TaskManager()

# Create task
task = manager.create_task(
    task_type="research",
    title="Research Ethereum scaling",
    description="Investigate scaling solutions",
    payload={"query": "Ethereum L2 rollups"}
)

# Assign to agent
manager.assign_task(task.id, "agent-002")

# Update status
manager.update_task_status(task.id, "in_progress", progress=0.5)

# Complete task
manager.complete_task(task.id, result={"summary": "Found 5 solutions"})
```

### Sending Messages

```python
from scripts.message_client import MessageClient, MessageType

client = MessageClient(agent_id="agent-001")

# Send task assignment
response = client.send_task_assignment(
    to_agent="agent-002",
    endpoint="https://agent-002.example.com/a2a",
    task_id="task-123",
    task_type="research",
    title="Research task",
    description="Test description",
    payload={"query": "test"}
)

# Send status update
response = client.send_status_update(
    to_agent="agent-001",
    endpoint="https://agent-001.example.com/a2a",
    task_id="task-123",
    status="in_progress",
    progress=0.5,
    message="Working on it"
)

# Send completion
response = client.send_task_completion(
    to_agent="agent-001",
    endpoint="https://agent-001.example.com/a2a",
    task_id="task-123",
    result={"summary": "Done"}
)
```

## CLI Usage

### Discovery

```bash
# Scan for agents
python scripts/discovery.py scan

# Fetch agent from URL
python scripts/discovery.py fetch --url https://agent.example.com

# List known agents
python scripts/discovery.py list

# Filter by capability
python scripts/discovery.py list --capability research

# Filter by task
python scripts/discovery.py list --task literature_review
```

### Agent Card

```bash
# Validate agent card
python scripts/agent_card.py validate agent-card.json

# Create agent card template
python scripts/agent_card.py create --name "My Agent" --id "agent-uuid"
```

### Task Lifecycle

```bash
# Create task
python scripts/task_lifecycle.py create \
    --type research \
    --title "Research task" \
    --description "Test" \
    --payload '{"query": "test"}'

# List all tasks
python scripts/task_lifecycle.py list

# List by state
python scripts/task_lifecycle.py list --state-filter in_progress

# List by agent
python scripts/task_lifecycle.py list --agent-filter agent-001

# Update task status
python scripts/task_lifecycle.py update task-123 --status in_progress --progress 0.5

# Complete task
python scripts/task_lifecycle.py complete task-123 --result '{"summary": "Done"}'

# Cancel task
python scripts/task_lifecycle.py cancel task-123 --reason "No longer needed"
```

### Message Client

```bash
# Send ping
python scripts/message_client.py send \
    --agent-id agent-001 \
    --target agent-002 \
    --endpoint https://agent-002.example.com/a2a \
    --type ping \
    --payload '{"nonce": "test"}'
```

## Testing

Run all unit tests:

```bash
python -m pytest tests/ -v
```

Run specific test suites:

```bash
python -m pytest tests/test_discovery.py
python -m pytest tests/test_agent_card.py
python -m pytest tests/test_task_lifecycle.py
python -m pytest tests/test_message_client.py
```

## File Structure

```
a2a-bridge/
├── SKILL.md                    # Main skill documentation
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── scripts/
│   ├── discovery.py            # Agent discovery module
│   ├── agent_card.py          # Agent Card parser
│   ├── task_lifecycle.py      # Task lifecycle manager
│   └── message_client.py      # Message client
├── references/
│   ├── a2a_protocol.md       # Protocol specification
│   └── agent_card_schema.md   # Agent Card schema
└── tests/
    ├── test_discovery.py
    ├── test_agent_card.py
    ├── test_task_lifecycle.py
    └── test_message_client.py
```

## Protocol Version

- **Current**: 1.0.0 (Phase 1 MVP)

## Message Types (Phase 1)

- `task_assignment` - Assign task to agent
- `status_update` - Update task progress
- `task_completion` - Report task completion
- `ping` - Health check

## Limitations (Phase 1)

- Private discovery only (no public registry)
- No authentication/encryption
- Basic message types only
- No retry logic (manual retry required)

## Next Steps

After Phase 1 completion:

1. Add authentication (JWT)
2. Implement public discovery registry
3. Add message encryption (JWE)
4. Implement retry logic with exponential backoff
5. Add more message types (file transfer, streaming)

## Troubleshooting

### Connection Errors

If you get connection errors:
- Verify agent endpoint is correct
- Check firewall settings
- Ensure agent is running and reachable

### Validation Errors

If validation fails:
- Check Agent Card format (see `references/agent_card_schema.md`)
- Verify message payload matches schema
- Check required fields are present

### Import Errors

If you get import errors:
- Install dependencies: `pip install -r requirements.txt`
- Add scripts to path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

## Support

For issues or questions:
- See protocol spec: `references/a2a_protocol.md`
- See agent card schema: `references/agent_card_schema.md`
- See SKILL.md for complete documentation
