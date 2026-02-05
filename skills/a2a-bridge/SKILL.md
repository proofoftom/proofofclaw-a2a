---
name: a2a-bridge
description: Agent-to-Agent (A2A) protocol implementation for inter-agent communication, task delegation, and collaboration. Use when working with multi-agent systems that need to: (1) Discover and communicate with other agents, (2) Parse and validate Agent Cards for capability matching, (3) Manage task lifecycle (assign, update, complete), (4) Send/receive A2A messages with proper validation.
metadata:
  {
    "openclaw":
      {
        "emoji": "🤝",
      },
  }
---

# A2A Bridge Skill

## Overview

A2A Bridge provides the client library and protocol implementation for Agent-to-Agent communication. It enables agents to discover each other, exchange capabilities via Agent Cards, and coordinate through a structured task lifecycle.

## Quick Start

### Basic Agent Discovery

Discover agents in your local network:

```python
from a2a_bridge import AgentDiscovery

discovery = AgentDiscovery()
agents = discovery.discover_local()
for agent in agents:
    print(f"Found: {agent.name} ({agent.id})")
```

### Send a Task

```python
from a2a_bridge import TaskClient

client = TaskClient()
task = client.create_task(
    target_agent_id="agent-123",
    task_type="research",
    payload={"query": "Ethereum scaling solutions"},
    priority="high"
)
```

### Process Incoming Tasks

```python
from a2a_bridge import TaskHandler

handler = TaskHandler()
handler.on_task_assigned(handle_task)
handler.start()
```

## Core Components

### 1. Agent Discovery (`scripts/discovery.py`)

Local agent discovery for finding nearby agents and their endpoints.

**Key functions:**
- `discover_local()` - Scan for agents on local network
- `register_self()` - Make current agent discoverable
- `get_agent_info(agent_id)` - Fetch agent details by ID

### 2. Agent Card Parser (`scripts/agent_card.py`)

Parse and validate Agent Cards - JSON documents describing an agent's capabilities.

**Agent Card Schema:**
```json
{
  "id": "agent-uuid",
  "name": "Agent Name",
  "version": "1.0.0",
  "capabilities": ["research", "coding", "writing"],
  "endpoint": "https://agent.example.com/a2a",
  "supported_tasks": ["task_type_1", "task_type_2"]
}
```

**Key functions:**
- `parse_agent_card(data)` - Parse and validate Agent Card
- `create_agent_card(**kwargs)` - Create Agent Card from fields
- `validate_capabilities(agent_card, required)` - Check if agent has required capabilities

### 3. Task Lifecycle (`scripts/task_lifecycle.py`)

Manage tasks through their complete lifecycle: creation, assignment, status updates, and completion.

**Task States:**
- `created` - Task created, not yet assigned
- `assigned` - Task assigned to an agent
- `in_progress` - Agent is actively working on task
- `completed` - Task finished successfully
- `failed` - Task failed with error
- `cancelled` - Task cancelled before completion

**Key functions:**
- `create_task(**kwargs)` - Create new task
- `assign_task(task_id, agent_id)` - Assign task to agent
- `update_task_status(task_id, status, **metadata)` - Update task status
- `complete_task(task_id, result)` - Mark task as completed
- `cancel_task(task_id, reason)` - Cancel a task

### 4. Message Client (`scripts/message_client.py`)

Send and receive A2A messages with proper validation and error handling.

**Message Types:**
- `task_assignment` - Assign a task to an agent
- `status_update` - Update task status
- `task_completion` - Report task completion
- `ping` - Simple health check/acknowledgment

**Key functions:**
- `send_message(target_agent_id, message_type, payload)` - Send message to agent
- `receive_message(timeout=30)` - Receive incoming message
- `validate_message(message)` - Validate message structure

## Usage Patterns

### Pattern 1: Capability-Based Task Routing

When you need to delegate a task to the most capable agent:

```python
from a2a_bridge import AgentDiscovery, TaskClient, AgentCard

# Find agents with required capability
discovery = AgentDiscovery()
agents = discovery.discover_local()

required_cap = "research"
eligible_agents = [
    agent for agent in agents
    if AgentCard.validate_capabilities(agent.card, [required_cap])
]

# Route task to first eligible agent
if eligible_agents:
    client = TaskClient()
    client.create_task(
        target_agent_id=eligible_agents[0].id,
        task_type="research",
        payload={...}
    )
```

### Pattern 2: Task Progress Tracking

Monitor task status across multiple agents:

```python
from a2a_bridge import TaskMonitor

monitor = TaskMonitor()
task_ids = [monitor.get_active_tasks()]

for task_id in task_ids:
    status = monitor.get_task_status(task_id)
    print(f"Task {task_id}: {status['state']}")
    if status['state'] == 'completed':
        result = monitor.get_task_result(task_id)
        # Process result...
```

### Pattern 3: Bidirectional Collaboration

Two agents working together on a complex task:

```python
# Agent A (initiator)
from a2a_bridge import TaskClient

client = TaskClient()
subtask1 = client.create_task(
    target_agent_id="agent-b-research",
    task_type="research",
    payload={"topic": "decentralized identity"}
)

subtask2 = client.create_task(
    target_agent_id="agent-c-analysis",
    task_type="analysis",
    payload={"depends_on": subtask1.id}
)

# Wait for dependencies...
client.wait_for_task(subtask1.id)
```

## Scripts Reference

### scripts/discovery.py

Agent discovery and registration.

```bash
# Scan for agents
python scripts/discovery.py scan

# Register current agent
python scripts/discovery.py register --agent-id <id> --endpoint <url>
```

### scripts/agent_card.py

Agent Card operations.

```bash
# Validate an Agent Card
python scripts/agent_card.py validate <path-to-card.json>

# Create Agent Card template
python scripts/agent_card.py create --name <name> --id <id>
```

### scripts/task_lifecycle.py

Task lifecycle management.

```bash
# Create task
python scripts/task_lifecycle.py create \
    --target <agent-id> \
    --type <task-type> \
    --payload <json-payload>

# Update task status
python scripts/task_lifecycle.py update <task-id> --status <status>

# Complete task
python scripts/task_lifecycle.py complete <task-id> --result <json-result>
```

### scripts/message_client.py

Direct message operations.

```bash
# Send message
python scripts/message_client.py send \
    --target <agent-id> \
    --type <message-type> \
    --payload <json-payload>

# Listen for messages
python scripts/message_client.py listen --timeout 60
```

## Protocol Specifications

See [A2A Protocol](references/a2a_protocol.md) for detailed protocol specifications including:
- Message format and validation rules
- Error handling and retry logic
- Security considerations
- Version compatibility

See [Agent Card Schema](references/agent_card_schema.md) for complete Agent Card schema definition.

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

Run specific test suite:

```bash
python -m pytest tests/test_discovery.py
python -m pytest tests/test_agent_card.py
python -m pytest tests/test_task_lifecycle.py
python -m pytest tests/test_message_client.py
```

## Integration with OpenClaw

To use A2A Bridge within an OpenClaw agent:

1. **Install dependencies** (handled by skill metadata)
2. **Configure agent endpoint** in OpenClaw config:
   ```json
   {
     "skills": {
       "entries": {
         "a2a-bridge": {
           "config": {
             "agentId": "your-agent-id",
             "endpoint": "https://your-agent.example.com/a2a",
             "discoveryEnabled": true
           }
         }
       }
     }
   }
   ```
3. **Initialize the bridge** in your agent's startup:
   ```python
   from a2a_bridge import A2ABridge

   bridge = A2ABridge(
       agent_id=config['agentId'],
       endpoint=config['endpoint']
   )
   bridge.start()
   ```

## Error Handling

All A2A Bridge functions raise specific exceptions:

- `AgentNotFoundError` - Target agent not found
- `InvalidMessageError` - Message validation failed
- `TaskNotFoundError` - Task ID doesn't exist
- `CapabilityMismatchError` - Agent lacks required capability
- `ConnectionError` - Failed to connect to agent endpoint

Always wrap A2A operations in try-except blocks for robust error handling.

## Limitations (Phase 1)

- **Private discovery only** - No public registry support yet
- **Basic message types** - Only task_assignment, status_update, task_completion, ping
- **No authentication** - Assumes trusted environment
- **No message encryption** - Plain HTTP for now

These will be addressed in future phases.

## Next Steps

After Phase 1 completion:
1. Add authentication & encryption
2. Implement public discovery registry
3. Add more message types (file transfer, streaming, etc.)
4. Build coordination primitives (workflows, dependencies)
