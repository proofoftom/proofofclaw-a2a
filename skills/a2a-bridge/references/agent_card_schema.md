# Agent Card Schema

## Version

1.0.0

## Overview

Agent Card is a JSON document that describes an AI agent's capabilities, endpoints, and metadata. It's the primary mechanism for capability discovery and matching in the A2A protocol.

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Card",
  "type": "object",
  "required": [
    "id",
    "name",
    "version",
    "capabilities",
    "endpoint",
    "supported_tasks"
  ],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique agent identifier (UUID v4)"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "Human-readable agent name"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Agent software version (semantic versioning)"
    },
    "description": {
      "type": "string",
      "maxLength": 500,
      "description": "Short description of the agent's purpose"
    },
    "capabilities": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "enum": [
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
      },
      "description": "List of general capabilities"
    },
    "endpoint": {
      "type": "string",
      "format": "uri",
      "description": "A2A endpoint URL (HTTP/HTTPS)"
    },
    "supported_tasks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 50
      },
      "description": "List of task types this agent can handle"
    },
    "supported_protocols": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^\\d+\\.\\d+\\.\\d+$"
      },
      "description": "Supported A2A protocol versions"
    },
    "owner": {
      "type": "string",
      "description": "Agent owner/organization identifier"
    },
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "busy", "offline"],
      "default": "active",
      "description": "Current agent status"
    },
    "max_concurrent_tasks": {
      "type": "integer",
      "minimum": 1,
      "default": 5,
      "description": "Maximum number of concurrent tasks"
    },
    "rate_limit": {
      "type": "object",
      "properties": {
        "requests_per_minute": {
          "type": "integer",
          "minimum": 1
        },
        "requests_per_hour": {
          "type": "integer",
          "minimum": 1
        }
      },
      "description": "Rate limiting configuration"
    },
    "metadata": {
      "type": "object",
      "description": "Custom metadata (key-value pairs)"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Tags for categorization and search"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Agent Card creation timestamp"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Agent Card last update timestamp"
    }
  }
}
```

## Example Agent Cards

### Example 1: Research Agent

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "proofofclaw-researcher",
  "version": "1.0.0",
  "description": "Research specialist for technical and domain knowledge gathering",
  "capabilities": ["research", "analysis"],
  "endpoint": "https://research.example.com/a2a",
  "supported_tasks": [
    "research",
    "literature_review",
    "fact_checking",
    "data_gathering"
  ],
  "supported_protocols": ["1.0.0"],
  "owner": "panarchi-team",
  "status": "active",
  "max_concurrent_tasks": 3,
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000
  },
  "tags": ["research", "knowledge", "academic"],
  "metadata": {
    "specialization": "blockchain and web3",
    "data_sources": ["arxiv", "github", "docs"],
    "language_preference": "en"
  },
  "created_at": "2024-02-01T00:00:00Z",
  "updated_at": "2024-02-05T10:00:00Z"
}
```

### Example 2: Coding Agent

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "proofofclaw-coder",
  "version": "1.0.0",
  "description": "Implementation specialist for software development",
  "capabilities": ["coding", "testing", "deployment"],
  "endpoint": "https://coder.example.com/a2a",
  "supported_tasks": [
    "implementation",
    "code_review",
    "bug_fixing",
    "testing",
    "deployment"
  ],
  "supported_protocols": ["1.0.0"],
  "owner": "panarchi-team",
  "status": "active",
  "max_concurrent_tasks": 5,
  "rate_limit": {
    "requests_per_minute": 120,
    "requests_per_hour": 2000
  },
  "tags": ["coding", "development", "engineering"],
  "metadata": {
    "primary_languages": ["Python", "JavaScript", "TypeScript"],
    "frameworks": ["React", "Node.js", "FastAPI"],
    "testing_tools": ["pytest", "jest"]
  },
  "created_at": "2024-02-01T00:00:00Z",
  "updated_at": "2024-02-05T10:00:00Z"
}
```

### Example 3: Writing Agent

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "proofofclaw-writer",
  "version": "1.0.0",
  "description": "Content specialist for documentation and communication",
  "capabilities": ["writing", "analysis"],
  "endpoint": "https://writer.example.com/a2a",
  "supported_tasks": [
    "documentation",
    "blog_post",
    "technical_writing",
    "summary",
    "editing"
  ],
  "supported_protocols": ["1.0.0"],
  "owner": "panarchi-team",
  "status": "active",
  "max_concurrent_tasks": 4,
  "tags": ["writing", "content", "communication"],
  "metadata": {
    "tone": "professional",
    "output_formats": ["markdown", "html", "pdf"],
    "languages": ["en", "es"]
  },
  "created_at": "2024-02-01T00:00:00Z",
  "updated_at": "2024-02-05T10:00:00Z"
}
```

## Capability Enumeration

### Built-in Capabilities

| Capability | Description |
|------------|-------------|
| `research` | Gather and analyze information from various sources |
| `analysis` | Perform data analysis and pattern recognition |
| `coding` | Write, review, and refactor code |
| `writing` | Create content, documentation, and narratives |
| `planning` | Create plans, roadmaps, and strategies |
| `monitoring` | Monitor systems, metrics, and alerts |
| `testing` | Write and execute tests |
| `deployment` | Deploy applications and infrastructure |
| `custom` | Custom capability (see metadata for details) |

### Custom Capabilities

Agents can declare `custom` capability and provide details in `metadata`:

```json
{
  "capabilities": ["custom"],
  "metadata": {
    "custom_capability_name": "blockchain_audit",
    "custom_capability_description": "Audits smart contracts for security vulnerabilities",
    "custom_capability_params": {
      "supported_chains": ["ethereum", "polygon"],
      "audit_depth": ["shallow", "deep"]
    }
  }
}
```

## Task Type Guidelines

### Task Type Naming

- Use snake_case
- Be descriptive but concise
- Match to agent's actual functionality
- Keep under 50 characters

### Common Task Types

```
research              - General research task
literature_review     - Academic literature review
fact_checking         - Verify facts and claims
data_gathering        - Collect and organize data
implementation        - Implement code or features
code_review           - Review code for quality
bug_fixing            - Identify and fix bugs
testing               - Write and run tests
deployment            - Deploy applications
documentation         - Write or update documentation
blog_post             - Create blog content
technical_writing     - Write technical documentation
summary               - Summarize content
editing               - Edit and improve content
analysis              - Analyze data or information
monitoring            - Monitor systems
planning              - Create plans or strategies
architecture          - Design system architecture
```

## Capability Matching

### Exact Match

```python
required = ["research", "analysis"]
agent_capabilities = ["research", "analysis", "writing"]
# Match: All required capabilities present
```

### Subset Match

```python
required = ["research"]
agent_capabilities = ["research", "analysis"]
# Match: Agent has all required capabilities (can have more)
```

### Failed Match

```python
required = ["deployment", "testing"]
agent_capabilities = ["research", "analysis"]
# No match: Agent lacks required capabilities
```

## Validation Rules

### Required Fields

- `id`: Must be valid UUID v4
- `name`: Non-empty string, max 100 chars
- `version`: Semantic versioning pattern
- `capabilities`: At least one capability
- `endpoint`: Valid URI
- `supported_tasks`: At least one task type

### Optional Fields Validation

- `status`: Must be one of enum values
- `max_concurrent_tasks`: Must be >= 1
- `rate_limit.requests_per_minute`: Must be >= 1
- `rate_limit.requests_per_hour`: Must be >= 1

### Metadata Validation

- `metadata` is free-form object
- No schema validation for custom keys
- Values can be strings, numbers, arrays, or objects

## Versioning

### Agent Card Version

The `version` field follows semantic versioning:
- **Major**: Breaking changes to capabilities/endpoint
- **Minor**: Non-breaking feature additions
- **Patch**: Bug fixes, metadata updates

### Schema Version

This schema itself is versioned. Current version: 1.0.0

Schema version changes:
- **Major**: Breaking changes (removed required fields, changed types)
- **Minor**: Added optional fields, relaxed constraints
- **Patch**: Documentation updates, minor corrections

## Best Practices

### 1. Be Specific with Capabilities

❌ Bad:
```json
{"capabilities": ["custom"]}
```

✅ Good:
```json
{
  "capabilities": ["research", "analysis"],
  "metadata": {
    "research_domains": ["blockchain", "web3"]
  }
}
```

### 2. Use Descriptive Task Types

❌ Bad:
```json
{"supported_tasks": ["task1", "task2", "task3"]}
```

✅ Good:
```json
{"supported_tasks": ["literature_review", "fact_checking", "data_gathering"]}
```

### 3. Keep Metadata Organized

Group related information:

```json
{
  "metadata": {
    "specialization": "blockchain research",
    "data_sources": ["arxiv", "github", "docs"],
    "language": "en",
    "output_formats": ["markdown", "json"]
  }
}
```

### 4. Update Timestamps

Always update `updated_at` when modifying the card:

```python
from datetime import datetime
card["updated_at"] = datetime.utcnow().isoformat() + "Z"
```

### 5. Version Your Changes

Update `version` when making breaking changes:

```python
card["version"] = "1.1.0"  # Minor version bump for new capability
```

## Discovery Mechanisms

### Static Discovery

Agent Cards served from a known location:
- HTTP endpoint: `https://agent.example.com/agent-card.json`
- File: Shared filesystem
- Config: Directly embedded in configuration

### Dynamic Discovery

Agents announce themselves:
- Broadcast on local network
- Register with discovery service
- Publish to event bus

### Peer-to-Peer

Agents share cards with each other:
- Direct exchange via A2A protocol
- Gossip protocol for propagation
- DHT (Distributed Hash Table) lookup

## References

- [A2A Protocol Specification](a2a_protocol.md)
- [Capability Matching Algorithm](#capability-matching)
- [Task Type Guidelines](#task-type-guidelines)
