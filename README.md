# Traefik MCP Server

A Model Context Protocol (MCP) server for managing and interacting with Traefik reverse proxy instances through AI assistants.

## Overview

This MCP server enables AI assistants to query and manage Traefik configurations, monitor service health, and perform administrative tasks through natural language interactions.

## Features

- 🔍 Query Traefik routers, services, and middlewares
- 📊 Get comprehensive Traefik overview and statistics
- ⚙️ View detailed configuration for individual components
- 🔒 Support for both API key and basic authentication
- 🚀 Async operations for optimal performance
- 🛠️ Provider-specific filtering (Docker, file, etc.)

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A running Traefik instance with API enabled

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd traefik-mcp
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Traefik API URL and credentials
   ```

## Configuration

Set the following environment variables:

### Required
- `TRAEFIK_API_URL`: URL of your Traefik API endpoint (e.g., `http://localhost:8080`)

### Authentication (choose one)
- `TRAEFIK_API_KEY`: API key for Bearer token authentication
- `TRAEFIK_BASIC_AUTH_USERNAME`: Username for basic authentication
- `TRAEFIK_BASIC_AUTH_PASSWORD`: Password for basic authentication

### Optional
- `MCP_LOG_LEVEL`: Logging level (default: INFO)

**Note**: API key authentication takes precedence over basic authentication if both are configured.

## Usage

### Running the Server

```bash
uv run traefik-mcp
```

### Integration with AI Clients

#### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "traefik": {
      "command": "/path/to/traefik-mcp/.venv/bin/traefik-mcp",
      "args": [],
      "env": {
        "TRAEFIK_API_URL": "http://localhost:8080",
        "TRAEFIK_BASIC_AUTH_USERNAME": "admin",
        "TRAEFIK_BASIC_AUTH_PASSWORD": "admin"
      }
    }
  }
}
```

#### Alternative (using uv)

```json
{
  "mcpServers": {
    "traefik": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/traefik-mcp",
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

### Available Tools

The MCP server provides the following tools:

- **`get_traefik_overview`**: Get comprehensive overview of all Traefik components
- **`list_routers`**: List all HTTP routers (optional provider filter)
- **`get_router_details`**: Get detailed configuration for a specific router
- **`list_services`**: List all HTTP services (optional provider filter)
- **`get_service_details`**: Get detailed configuration for a specific service
- **`list_middlewares`**: List all HTTP middlewares (optional provider filter)

### Example Usage

Once configured with Claude Desktop, you can ask questions like:
- "Show me all routers in my Traefik setup"
- "What services are running behind the traefik.test router?"
- "List all middlewares configured for Docker provider"
- "Give me an overview of my Traefik instance"

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Troubleshooting

### Common Issues

**Server shows 0 routers/services**
- Ensure your Traefik API is accessible at the configured URL
- Verify authentication credentials are correct
- Check that Traefik API is enabled in your configuration

**Authentication failures**
- Verify basic auth credentials match your Traefik configuration
- If using API key, ensure it's correctly formatted
- API key takes precedence over basic auth if both are set

**Connection errors**
- Check that `TRAEFIK_API_URL` is reachable from the MCP server
- Verify Traefik is running and API is enabled
- Check network/firewall settings

### Testing the Server

You can test the MCP server manually:

```bash
# Set environment variables and run
export TRAEFIK_API_URL="http://localhost:8080"
export TRAEFIK_BASIC_AUTH_USERNAME="admin"
export TRAEFIK_BASIC_AUTH_PASSWORD="admin"
uv run traefik-mcp
```

## Project Status

✅ **Phase 1 Complete** - Core functionality implemented
- Traefik API integration with authentication
- All query tools working correctly
- Support for both API key and basic authentication
- Comprehensive error handling

🚧 **Phase 2 Planned** - Management features
- Dynamic configuration updates
- Service health monitoring
- Advanced filtering and search

See [TASKS.md](TASKS.md) for current development tasks and [PLANNING.md](PLANNING.md) for project roadmap.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - See LICENSE file for details

## Resources

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)