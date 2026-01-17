# Traefik MCP Server - Initial Tasks

## Phase 1: Project Setup & Foundation

### Task 1: Environment Setup
**Priority**: High

- [ ] Install `uv` package manager
- [ ] Create project structure using `uv init traefik-mcp-server`
- [ ] Set up virtual environment with `uv venv`
- [ ] Configure `pyproject.toml` with project metadata and dependencies

**Dependencies to add:**
```bash
uv add "mcp[cli]" httpx pyyaml pydantic python-dotenv
```

**Dev dependencies:**
```bash
uv add --dev pytest pytest-asyncio pytest-cov black ruff mypy
```

**Deliverable**: Working Python project with dependencies installed

---

### Task 2: Create Project Structure
**Priority**: High

- [ ] Create directory structure as outlined in PLANNING.md
- [ ] Add `__init__.py` files to all package directories
- [ ] Create `.env.example` with configuration template
- [ ] Set up `.gitignore` for Python projects
- [ ] Initialize git repository

**Deliverable**: Complete project skeleton

---

### Task 3: Traefik API Client - Basic Implementation
**Priority**: High

**File**: `src/traefik_mcp/traefik/api_client.py`

- [ ] Create `TraefikClient` class with async httpx client
- [ ] Implement connection/authentication logic (API key if provided)
- [ ] Implement basic GET endpoints:
  - [ ] `get_overview()` - GET /api/overview
  - [ ] `get_routers()` - GET /api/http/routers
  - [ ] `get_services()` - GET /api/http/services
  - [ ] `get_middlewares()` - GET /api/http/middlewares
- [ ] Add error handling and retries
- [ ] Implement connection health check
- [ ] Add logging

**Example structure:**
```python
class TraefikClient:
    def __init__(self, api_url: str, api_key: str = None):
        """
        Initialize Traefik API client.
        
        Args:
            api_url: Base URL for Traefik API (e.g., http://localhost:8080)
            api_key: Optional API key for authentication
        """
        pass
    
    async def get_overview(self) -> dict:
        """Get Traefik overview."""
        pass
    
    async def get_routers(self, provider: str = None) -> list[dict]:
        """Get all HTTP routers."""
        pass
```

**Deliverable**: Working API client that can query Traefik

---

### Task 4: Data Models
**Priority**: High

**File**: `src/traefik_mcp/traefik/models.py`

- [ ] Create Pydantic models for Traefik entities:
  - [ ] `Router` model
  - [ ] `Service` model
  - [ ] `Middleware` model
  - [ ] `EntryPoint` model
  - [ ] `Provider` model
- [ ] Add validation rules
- [ ] Add serialization methods for MCP responses

**Deliverable**: Type-safe models for all Traefik entities

---

### Task 5: MCP Server Setup
**Priority**: High

**File**: `src/traefik_mcp/server.py`

- [ ] Create main MCP server instance
- [ ] Set up server initialization with configuration
- [ ] Implement basic server lifecycle (start/stop)
- [ ] Add connection to Traefik API client
- [ ] Set up logging configuration
- [ ] Create main entry point in `__main__.py`

**Example structure:**
```python
from mcp.server import Server
import mcp.types as types

server = Server("traefik-mcp")
traefik_client = None

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [...]

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
```

**Deliverable**: MCP server that can start and accept connections

---

## Phase 1: Core Tools Implementation

### Task 6: Query Tools - Read Operations
**Priority**: High

**File**: `src/traefik_mcp/tools/query_tools.py`

Implement the following MCP tools:

- [ ] `list_routers` - List all HTTP/TCP routers
  - Parameters: `provider` (optional), `status` (optional)
  - Returns: Formatted list of routers with key details
  
- [ ] `list_services` - List all services
  - Parameters: `provider` (optional)
  - Returns: Formatted list of services
  
- [ ] `list_middlewares` - List all middlewares
  - Parameters: `provider` (optional)
  - Returns: Formatted list of middlewares
  
- [ ] `get_overview` - Get complete Traefik status
  - Returns: Summary of routers, services, middlewares counts
  
- [ ] `get_router_details` - Get specific router configuration
  - Parameters: `router_name` (required), `provider` (optional)
  - Returns: Detailed router configuration
  
- [ ] `get_service_details` - Get specific service configuration
  - Parameters: `service_name` (required), `provider` (optional)
  - Returns: Detailed service configuration

**Each tool should:**
- Have clear description for AI understanding
- Validate input parameters
- Format responses for readability
- Handle errors gracefully

**Deliverable**: 6 working read-only tools

---

### Task 7: Resources Implementation
**Priority**: Medium

**File**: `src/traefik_mcp/resources/traefik_data.py`

- [ ] Implement `current-config` resource
  - Returns: Complete current Traefik configuration
  - Include: routers, services, middlewares, entrypoints
  
- [ ] Implement `routers-list` resource
  - Returns: Catalog of all routers with metadata
  
- [ ] Implement `health-status` resource
  - Returns: Current health status of Traefik

**Deliverable**: 3 MCP resources providing Traefik data

---

### Task 8: Testing Infrastructure
**Priority**: High

- [ ] Set up pytest configuration in `pyproject.toml`
- [ ] Create test fixtures for mock Traefik responses
- [ ] Write unit tests for `TraefikClient`:
  - [ ] Test connection with auth
  - [ ] Test each API method
  - [ ] Test error handling
- [ ] Write unit tests for tools:
  - [ ] Test each tool's execution
  - [ ] Test parameter validation
- [ ] Set up GitHub Actions or similar CI
- [ ] Configure coverage reporting

**Test file structure:**
```
tests/
├── test_api_client.py
├── test_query_tools.py
├── fixtures/
│   └── mock_responses.json
```

**Deliverable**: Test suite with >70% coverage

---

### Task 9: Documentation - Phase 1
**Priority**: Medium

- [ ] Write comprehensive README.md:
  - [ ] Project overview
  - [ ] Quick start guide
  - [ ] Installation instructions
  - [ ] Basic usage example
  
- [ ] Create `docs/setup.md`:
  - [ ] Environment setup
  - [ ] Traefik configuration requirements (enabling API)
  - [ ] AI client integration instructions
  - [ ] Single instance configuration
  
- [ ] Write `.env.example` with configuration options:
  ```bash
  # Required: Traefik API URL
  TRAEFIK_API_URL=http://localhost:8080
  
  # Optional: API Key (only if your Traefik instance requires it)
  # TRAEFIK_API_KEY=your-api-key-here
  
  # Optional: Logging
  MCP_LOG_LEVEL=INFO
  ```
  
- [ ] Create example AI client configurations in `examples/` (Claude Desktop, Cline, etc.)

**Deliverable**: Complete setup documentation

---

### Task 10: Integration with AI Client
**Priority**: High

- [ ] Test MCP server with an AI client (such as Claude Desktop, Cline, or other MCP-compatible client)
- [ ] Create configuration file for the AI client
- [ ] Verify all tools work correctly
- [ ] Test error scenarios
- [ ] Document any issues or limitations

**AI Client config example:**
```json
{
  "mcpServers": {
    "traefik": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/traefik-mcp-server",
        "run",
        "traefik-mcp"
      ],
      "env": {
        "TRAEFIK_API_URL": "http://localhost:8080"
      }
    }
  }
}
```

**Note**: Only add `TRAEFIK_API_KEY` to the `env` object if your Traefik instance requires authentication.

**Deliverable**: Working integration with AI client

---

## Quick Start Checklist

To get started quickly, complete tasks in this order:

1. ✅ Task 1: Environment Setup
2. ✅ Task 2: Create Project Structure
3. ✅ Task 3: Traefik API Client
4. ✅ Task 4: Data Models
5. ✅ Task 5: MCP Server Setup
6. ✅ Task 6: Query Tools (start with just 2-3 tools)
7. ✅ Task 10: Integration with AI Client (test early!)
8. ✅ Task 8: Testing Infrastructure
9. ✅ Task 7: Resources Implementation
10. ✅ Task 9: Documentation

---

## Optional Quick Wins

These tasks can be done after Phase 1 to add immediate value:

### Task 11: Prompts for Common Operations
**Priority**: Low

**File**: `src/traefik_mcp/prompts/traefik_prompts.py`

- [ ] Create `create-route` prompt template
- [ ] Create `troubleshoot-503` prompt template
- [ ] Create `check-security` prompt template

---

### Task 12: Configuration Parser
**Priority**: Medium

**File**: `src/traefik_mcp/traefik/config_parser.py`

- [ ] Implement YAML configuration parser
- [ ] Implement TOML configuration parser
- [ ] Add validation for parsed configurations
- [ ] Support reading from file system

This enables file-based provider support.

---

### Task 13: Enhanced Error Messages
**Priority**: Low

- [ ] Create custom exception classes
- [ ] Add user-friendly error messages
- [ ] Include troubleshooting hints in errors
- [ ] Add context to API errors

---

## Development Environment Recommendations

### Recommended Setup
- **IDE**: VS Code or PyCharm
- **Python**: 3.10 or higher
- **Traefik**: Version 3.x (for testing)
- **OS**: Linux/macOS preferred (Windows with WSL2)

### Useful VS Code Extensions
- Python
- Pylance
- Ruff
- Even Better TOML
- YAML

### Local Testing Environment

Set up a local Traefik instance with Docker:

```bash
# docker-compose.yml
version: '3'

services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      
  whoami:
    image: traefik/whoami
    labels:
      - "traefik.http.routers.whoami.rule=Host(`whoami.localhost`)"
```

---

---

## Success Criteria for Phase 1 Completion

- [ ] MCP server starts without errors
- [ ] Can connect to Traefik API successfully
- [ ] All 6 query tools work correctly
- [ ] Can query Traefik through an AI client
- [ ] Tests pass with >70% coverage
- [ ] Documentation allows new user to set up in <10 minutes
- [ ] No critical bugs or crashes

---

## Next Steps After Phase 1

Once Phase 1 is complete, proceed to:

1. **Phase 2**: Implement configuration write operations (create/update/delete)
2. **User Feedback**: Get feedback from initial users
3. **Enhanced Features**: Add monitoring tools
4. **Production Hardening**: Security audit, performance optimization

---

## Getting Help

- **Traefik Documentation**: https://doc.traefik.io/traefik/
- **MCP Documentation**: https://modelcontextprotocol.io/
- **MCP Python SDK Examples**: https://github.com/modelcontextprotocol/python-sdk/tree/main/examples
- **Community**: Create GitHub Discussions for questions