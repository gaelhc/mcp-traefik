"""
Main entry point for the Traefik MCP server.

This module provides command-line entry points for running the
Traefik Model Context Protocol (MCP) server with stdio or SSE transport.
"""
import os
import logging
import ipaddress
from typing import Optional
from traefik_mcp.server import mcp

# Configure logging
log_level = os.getenv('MCP_LOG_LEVEL','INFO').strip(' "\'').upper()
valid_log_level = log_level in ['INFO','WARNING','DEBUG','ERROR']
if not valid_log_level: log_level = 'INFO'


logging.basicConfig(level=log_level,format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
if not valid_log_level:
    logger.warning("Invalid 'MCP_LOG_LEVL', must be 'INFO','WARNING','DEBUG' or 'ERROR'.\n")
logger.info(f'Log level: {log_level}')


def _get_port() -> int:
    """
    Get and validate the MCP server port.
    
    Returns:
        Valid integer port number
        
    Raises:
        ValueError: If port is not a valid integer or out of range
    """
    port_str = os.getenv('MCP_PORT', '8080').strip(' "\'')
    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError(f"Invalid MCP_PORT: : {port}. Must be between 1 and 65535.")
    except Exception as e:
        raise ValueError(f"Invalid MCP_PORT: {port_str!r}.")

    return port
    
def _get_host() -> str:
    """
    Get the MCP server host address.
    
    Returns:
        Host address (default: '0.0.0.0')
    """
    def checkIP(ip_str: str) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
            return isinstance(ip, ipaddress.IPv4Address)
        except ValueError:
            return False
        
    host = os.getenv('MCP_HOST', '0.0.0.0').strip(' "\'')
    if not checkIP(host):
        raise ValueError(f"Invalid MCP_HOST : '{host}' not a valid IPv4 address.")
        
    return host

def _get_transport() -> str:
    """
    Get the MCP server transport mode.
    
    Returns:
        MCP transport mode (default: 'stdio')
    """
    transport_mode = os.getenv('MCP_TRANSPORT', 'stdio').strip(' "\'').lower()
    if not transport_mode in ['stdio', 'sse']:
        raise ValueError(f"Invalid MCP_TRANSPORT: '{transport_mode}' must be 'stdio' or 'sse'")
    
    return transport_mode

def main() -> None:
    """Entry point for the traefik-mcp command.
    
    Reads configuration from environment variables and starts the MCP server.
    
    Environment variables:
        MCP_TRANSPORT: Transport mode ('stdio' or 'sse', default: 'stdio')
        MCP_HOST: Host address for SSE transport (default: '0.0.0.0')
        MCP_PORT: Port number for SSE transport (default: 8080)
    """
    mcp_transport: str = _get_transport()
    mcp_host: Optional[str] = _get_host()
    mcp_port: int = _get_port()
    
    logger.info("Traefik MCP server starting...")
    logger.info(f"Transport mode: {mcp_transport}")
    
    if mcp_transport == 'stdio':
        logger.info("Starting stdio transport")
        mcp.run(transport='stdio')
    elif mcp_transport == 'sse':
        mcp_host = _get_host()
        logger.info(f"Starting SSE transport on {mcp_host}:{mcp_port}")
        mcp.run(transport="sse", host=mcp_host, port=mcp_port)


if __name__ == "__main__":
    main()
