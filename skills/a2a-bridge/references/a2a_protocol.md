# A2A Protocol Specification

## Version

1.0.0 (Phase 1 - MVP)

## Overview

The Agent-to-Agent (A2A) protocol enables secure, structured communication between AI agents. This specification defines message formats, validation rules, and best practices for inter-agent collaboration.

## Core Concepts

### Messages

All A2A communication uses JSON messages with a standardized envelope:

```json
{
  "version": "1.0.0",
  "message_id": "msg-uuid-v4",
  "timestamp": "2024-02-05T15:30:00Z",
  "from": "agent-uuid-v4",
  "to": "agent-uuid-v4",
  "type": "task_assignment",
  "payload": { ... },
  "signature": "base64-encoded-signature"
}
```

### Message Types (Phase 1)

#### task_assignment

Assigns a task to a target agent.

```json
{
  "version": "1.0.0",
  "message_id": "msg-123",
  "timestamp": "2024-02-05T15:30:00Z",
  "from": "agent-001",
  "to": "agent-002",
  "type": "task_assignment",
  "payload": {
    "task_id": "task-456",
    "task_type": "research",
    "title": "Research Ethereum scaling",
    "description": "Investigate current scaling solutions",
    "payload": {
      "query": "Ethereum scaling solutions L2 rollups",
      "depth": "deep"
    },
    "priority": "high",
    "deadline": "2024-02-05T18:00:00Z",
    "metadata": {
      "source": "user_request",
      "session_id": "sess-789"
    }
  }
}
```

**Payload fields:**
- `task_id` (required, string): Unique task identifier
- `task_type` (required, string): Type of task (must match target agent's `supported_tasks`)
- `title` (required, string): Human-readable task title
- `description` (required, string): Detailed task description
- `payload` (required, object): Task-specific data
- `priority` (optional, string): One of `low`, `medium`, `high`, `urgent` (default: `medium`)
- `deadline` (optional, ISO8601): Task deadline
- `metadata` (optional, object): Additional metadata

#### status_update

Updates the status of an assigned task.

```json
{
  "version": "1.0.0",
  "message_id": "msg-124",
  "timestamp": "2024-02-05T15:45:00Z",
  "from": "agent-002",
  "to": "agent-001",
  "type": "status_update",
  "payload": {
    "task_id": "task-456",
    "status": "in_progress",
    "progress": 0.5,
    "message": "Gathering sources...",
    "metadata": {
      "sources_found": 12
    }
  }
}
```

**Payload fields:**
- `task_id` (required, string): Task identifier
- `status` (required, string): One of `created`, `assigned`, `in_progress`, `completed`, `failed`, `cancelled`
- `progress` (optional, number): Progress value 0.0-1.0
- `message` (optional, string): Human-readable status message
- `metadata` (optional, object): Additional metadata

#### task_completion

Reports that a task has been completed.

```json
{
  "version": "1.0.0",
  "message_id": "msg-125",
  "timestamp": "2024-02-05T16:30:00Z",
  "from": "agent-002",
  "to": "agent-001",
  "type": "task_completion",
  "payload": {
    "task_id": "task-456",
    "status": "completed",
    "result": {
      "summary": "Found 5 main scaling solutions",
      "findings": [...],
      "sources": [...]
    },
    "execution_time_ms": 3600000,
    "metadata": {
      "confidence": 0.95
    }
  }
}
```

**Payload fields:**
- `task_id` (required, string): Task identifier
- `status` (required, string): Always `completed` or `failed`
- `result` (required, object): Task result data
- `execution_time_ms` (optional, number): Execution time in milliseconds
- `metadata` (optional, object): Additional metadata

#### ping

Simple health check/acknowledgment.

```json
{
  "version": "1.0.0",
  "message_id": "msg-126",
  "timestamp": "2024-02-05T16:35:00Z",
  "from": "agent-001",
  "to": "agent-002",
  "type": "ping",
  "payload": {
    "nonce": "random-string",
    "echo": "optional-data-to-echo-back"
  }
}
```

**Payload fields:**
- `nonce` (required, string): Random nonce for correlation
- `echo` (optional, any): Optional data to echo back in response

## Validation Rules

### Envelope Validation

- `version` must be `"1.0.0"` (for Phase 1)
- `message_id` must be a valid UUID v4
- `timestamp` must be valid ISO8601 format
- `from` and `to` must be valid UUID v4s
- `type` must be one of the defined message types
- `payload` must be a JSON object

### Payload Validation

Each message type has specific validation rules as defined above. Unknown fields in payload are **not allowed** (strict mode).

### Response Requirements

Agents must respond to messages within reasonable time:
- `task_assignment`: Must acknowledge within 30 seconds
- `status_update`: No response required (fire-and-forget)
- `task_completion`: Must acknowledge within 10 seconds
- `ping`: Must echo back with same nonce

## Error Handling

### Error Messages

When a message cannot be processed, the receiving agent should send an error response:

```json
{
  "version": "1.0.0",
  "message_id": "msg-127",
  "timestamp": "2024-02-05T16:40:00Z",
  "from": "agent-002",
  "to": "agent-001",
  "type": "error",
  "payload": {
    "original_message_id": "msg-123",
    "error_code": "INVALID_TASK_TYPE",
    "error_message": "Task type 'research' not supported by this agent",
    "details": {
      "supported_types": ["analysis", "writing"]
    }
  }
}
```

### Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_MESSAGE_FORMAT` | Message format is invalid |
| `UNSUPPORTED_MESSAGE_TYPE` | Message type not supported |
| `INVALID_TASK_TYPE` | Task type not supported by agent |
| `TASK_NOT_FOUND` | Task ID doesn't exist |
| `AGENT_NOT_FOUND` | Target agent doesn't exist |
| `CAPABILITY_MISMATCH` | Agent lacks required capability |
| `PAYLOAD_VALIDATION_FAILED` | Payload failed validation |
| `TIMEOUT` | Operation timed out |
| `INTERNAL_ERROR` | Unexpected error |

## Retry Logic

### Retryable Errors

Clients should retry on these errors:
- `TIMEOUT`
- `INTERNAL_ERROR`
- Network-level errors (connection refused, DNS resolution failed)

### Non-Retryable Errors

Do NOT retry on these errors:
- `INVALID_MESSAGE_FORMAT`
- `UNSUPPORTED_MESSAGE_TYPE`
- `INVALID_TASK_TYPE`
- `CAPABILITY_MISMATCH`

### Retry Strategy

- **Exponential backoff**: Start at 1 second, double each retry
- **Max retries**: 3 attempts
- **Max total wait time**: 15 seconds

## Security Considerations (Phase 1)

### Current Limitations

Phase 1 operates in a **trusted environment** with:
- No authentication
- No message encryption
- No replay protection
- No authorization checks

### Best Practices

Even without full security:

- Use HTTPS endpoints to protect in transit
- Validate all messages before processing
- Log all messages for audit trails
- Rate-limit incoming messages
- Implement timeouts for all operations

### Future Enhancements

Future phases will add:
- JWT-based authentication
- Message-level encryption (JWE)
- Replay protection via message IDs
- Capability-based authorization

## Transport

### HTTP/HTTPS

Phase 1 uses standard HTTP/HTTPS:

```
POST /a2a/messages HTTP/1.1
Host: agent.example.com
Content-Type: application/json

{...message...}
```

**Response codes:**
- `200 OK`: Message accepted
- `400 Bad Request`: Invalid message format
- `404 Not Found`: Agent or task not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### WebSocket (Future)

WebSocket support planned for real-time communication in future phases.

## Version Compatibility

### Protocol Versioning

- `version` field in envelope
- Major version changes are breaking
- Minor version changes add non-breaking features
- Patch version changes are bug fixes only

### Backward Compatibility

Agents must support:
- The latest protocol version
- At least one previous major version (if applicable)

## Testing

### Test Scenarios

1. **Message validation**: Send invalid messages, expect errors
2. **Task lifecycle**: Full flow: create → assign → update → complete
3. **Error handling**: Simulate errors, verify correct responses
4. **Retry logic**: Test retry strategy with network failures
5. **Concurrent messages**: Send multiple messages simultaneously

## References

- [Agent Card Schema](agent_card_schema.md)
- [Task Lifecycle States](#task-states)
- [Message Type Examples](#message-types-phase-1)
