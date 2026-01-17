# Traefik MCP Server

A Model Context Protocol (MCP) server for managing and interacting with Traefik reverse proxy instances through AI assistants.

## Overview

This MCP server enables AI assistants to query and manage Traefik configurations, monitor service health, and perform administrative tasks through natural language interactions.

## Features

- 🔍 Query Traefik routers, services, and middlewares
- 📊 Monitor service health and metrics
- ⚙️ Manage Traefik configuration dynamically
- 🔒 Secure API authentication support
- 🚀 Async operations for performance

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A running Traefik instance with API enabled

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd traefik-mcp-server
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

- `TRAEFIK_API_URL` (required): URL of your Traefik API endpoint
- `TRAEFIK_API_KEY` (optional): API key if authentication is required
- `MCP_LOG_LEVEL` (optional): Logging level (default: INFO)

## Usage

### Running the Server

```bash
uv run traefik-mcp
```

### Integration with AI Clients

Add to your AI client's MCP configuration:

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

## Project Status

🚧 **In Development** - Phase 1 (MVP) in progress

See [TASKS.md](TASKS.md) for current development tasks and [PLANNING.md](PLANNING.md) for project roadmap.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - See LICENSE file for details

## Resources

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)