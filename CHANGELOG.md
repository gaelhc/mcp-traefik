# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive authentication testing suite
- Manual MCP server testing script for debugging
- Detailed troubleshooting documentation in README
- Example usage documentation with Claude Desktop integration

### Fixed
- **Critical**: API client methods incorrectly calling `.values()` on list responses
- **Critical**: QueryTools expecting dictionary format but receiving lists from API
- **Critical**: TraefikOverview model expecting flat structure but API returns nested `http/tcp/udp` sections
- **Critical**: MCP server reporting 0 routers/services despite active Traefik configuration
- Updated README configuration examples for proper Claude Desktop integration
- Fixed project name references from `traefik-mcp-server` to `traefik-mcp`

### Changed
- Updated TraefikOverview model to correctly parse API response structure
- Modified QueryTools to handle list-based API responses
- Enhanced README with comprehensive configuration and troubleshooting sections
- Improved authentication documentation with clear precedence rules

### Security
- Confirmed basic authentication implementation is secure and working correctly
- Verified API key authentication takes precedence over basic auth as intended

---

## [0.1.0] - 2025-01-17

### Added
- Initial MCP server implementation for Traefik integration
- Support for both API key and basic authentication
- Core query tools for routers, services, and middlewares
- Traefik overview and statistics functionality
- Provider-specific filtering capabilities
- Async HTTP client with proper error handling
- Pydantic models for Traefik entities
- Comprehensive test suite
- Claude Desktop integration examples

### Features
- **Query Tools**:
  - `get_traefik_overview` - Comprehensive Traefik statistics
  - `list_routers` - List all HTTP routers with provider filtering
  - `get_router_details` - Detailed router configuration
  - `list_services` - List all HTTP services with provider filtering  
  - `get_service_details` - Detailed service configuration
  - `list_middlewares` - List all HTTP middlewares with provider filtering

- **Authentication**:
  - Bearer token (API key) authentication
  - Basic authentication support
  - Automatic authentication method detection
  - Secure credential handling

- **Integration**:
  - Model Context Protocol (MCP) compliant server
  - Claude Desktop integration
  - JSON-RPC communication
  - Structured error responses

### Infrastructure
- Python 3.10+ support
- uv package manager integration
- pytest testing framework
- black code formatting
- ruff linting
- mypy type checking
- Comprehensive documentation

---

## [0.0.1] - Development

### Added
- Project initialization
- Basic structure and configuration
- Development environment setup
