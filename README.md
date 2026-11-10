# Traefik MCP Server

A Model Context Protocol (MCP) server for Traefik reverse proxy instances.
> Forked from `theupriser/treafik-mcp`


## Overview

This MCP server enables AI assistants to query and inject Traefik configurations in LLM context window.

## Features

- 🔍 Query Traefik *entrypoints*, *routers*, *services*, and *middlewares*
- 📊 Get comprehensive configuration and statistics in markdown format
- ⚙️ View summary lists or detailed configuration for individual components
- ⚙️ Support *stdio* or *http/sse* transport
- 🚀 Run locally or in Docker container

### Work in progress
- 🔒 Support for both API key and basic authentication for containerized deployment


## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A running Traefik instance with Dashboard enabled

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp-traefik
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
   # Edit .env with your own configuration
   ```

3. Run locally:
   ```bash
   python -m traefik_mcp.server
   ```

### Docker container

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp-traefik
   ```

2. Adapt `docker-compose.yml` environment and run:
   ```bash
   docker compose up -d
   ```
> Docker container setup only support `http/sse`transport

## Configuration

Set the following environment variables:

### Required
- `TRAEFIK_API_URL`: URL of your Traefik Dashboard endpoint (e.g., `http://localhost:8080`)

### Transport
- `MCP_TRANSPORT`: Type of transport, must be 'stdio' or 'http'
- `MCP_HOST`: Host IP adres, default '0.0.0.0' (for 'http' transport only)
- `MCP_PORT`: Host port, default '8080' (for 'http' transport only)

### Authentication (choose one)
- `TRAEFIK_API_KEY`: API key for Bearer token authentication
- `TRAEFIK_BASIC_AUTH_USERNAME`: Username for basic authentication
- `TRAEFIK_BASIC_AUTH_PASSWORD`: Password for basic authentication

### Optional
- `MCP_LOG_LEVEL`: Logging level (default: INFO)


**Note**: API key authentication takes precedence over basic authentication if both are configured.


## Integration with AI Clients

### VSCode integration

Add to your VSCode configuration file (e.g. `.vscode/mcp.json`):

#### Local
```json
{
  "servers": {
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

#### Distant deployment in Docker container
```json
{
  "servers": {
    "traefik": {
      "url": "http://localhost:8080/mcp/sse"
      }
    }
  }
}
```

#### Local alternative using uv

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
- **`get_version`**: Get version of Traefik instance
- **`get_entrypoint`**: Get a summarized list of entrypoints, or a detailled report of a given entrypoint
- **`get_router`**: Get a summarized list of routers, or a detailled report of a given router, for *http*, *tcp*, and *udp* protocols
- **`get_service`**: Get a summarized list of services, or a detailled report of a given service, for *http*, *tcp*, and *udp* protocols
- **`get_middleware`**: Get a summarized list of middlewares, or a detailled report of a given middleware, for *http*, *tcp*, and *udp* protocols


### Example Usage

Once configured, you can ask questions like:
- "Show me all routers in my Traefik setup"
- "What services are running behind the traefik.test router?"
- "List all middlewares configured for Docker provider"
- "Give me an overview of my Traefik instance"
- "Is my Traefik configuration secured ?"

See `QUALIFICATION.md` for an integration test in french ;).

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

## Contributing

Contributions are welcome! Do not hesitate to propose pull request. Just make sure to conform with Code architecture, formats and tests.

Consult `.windsurf/rules/project-rules.md`.

## License

This depot is a fork from `https://github.com/theupriser/treafik-mcp`.
Please visit this original depot for more informations about original commits.

MIT License - See LICENSE file for details

## Resources

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)