"""
Traefik MCP Server

A Model Context Protocol server for managing Traefik reverse proxy instances.
Supports both stdio and HTTP/SSE transports via environment variable control.
Uses Starlette ASGI app for HTTP mode with proper SSE routing.
"""

import asyncio
import logging
import os

import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
    CallToolRequestParams,
    PaginatedRequestParams,
)

import mcp.server.stdio
import mcp.server.sse

from .traefik.api_client import TraefikClient
from .tools.query_tools import QueryTools


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global variables
traefik_client: TraefikClient | None = None
query_tools: QueryTools | None = None


# ---------------------------------------------------------
# MCP Tool definitions
# ---------------------------------------------------------

async def list_tools(
    ctx,
    params: PaginatedRequestParams | None = None,
) -> ListToolsResult:
    """List available tools."""

    tools = [
        Tool(
            name="get_overview",
            description="Get an overview of the Traefik instance configuration",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_version",
            description="Get the Traefik API version",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_entrypoint",
            description="Get informations about entrypoints",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "[Optional] Name of the entrypoint (return detailled informations)"
                    },
                },
                "required": []
            }
        ),
        Tool(
            name="get_middleware",
            description="Get information about middlewares",
            inputSchema={
                "type": "object",
                "properties": {
                    "protocol": {
                        "type": "string",
                        "description": "Protocol of the middleware, in ['http', 'tcp', 'udp']"
                    },
                    "name": {
                        "type": "string",
                        "description": """Name of the middleware including its provider i.e. `name@provider`
                                          Returns detailled informations about the middleware
                                          Consult `get_service` without name for list of middlewares
                                          """
                    }
                },
                "required": ["protocol"]
            }
        ),
        Tool(
            name="get_service",
            description="Get information about services",
            inputSchema={
                "type": "object",
                "properties": {
                    "protocol": {
                        "type": "string",
                        "description": "Protocol of the service, in ['http', 'tcp', 'udp']"
                    },
                    "name": {
                        "type": "string",
                        "description": """Name of the service including its provider i.e. `name@provider`
                                          Returns detailled informations about the service
                                          Consult `get_service` without name for list of services
                                          """
                    }
                },
                "required": ["protocol"]
            }
        ),
        Tool(
            name="get_router",
            description="Get information about routers",
            inputSchema={
                "type": "object",
                "properties": {
                    "protocol": {
                        "type": "string",
                        "description": "Protocol of the router, in ['http', 'tcp', 'udp']"
                    },
                    "name": {
                        "type": "string",
                        "description": """Name of the router including its provider i.e. `name@provider`
                                          Returns detailled informations about the router
                                          Consult `get_router` without name for list of routers
                                          """
                    }
                },
                "required": ["protocol"]
            }
        )
    ]

    return ListToolsResult(tools=tools)


async def call_tool(
    ctx,
    params: CallToolRequestParams,
) -> CallToolResult:
    """Handle tool calls."""

    name = params.name
    args = params.arguments or {}

    if not query_tools:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Traefik client not initialized. Please check your configuration."
                )
            ],
            isError=True
        )

    try:
        if name == "get_overview":
            result = await query_tools.get_overview()

        elif name == "get_version":
            result = await query_tools.get_version()

        elif name == "get_entrypoint":
            result = await query_tools.get_entrypoint(name=args.get('name', None))

        elif name == "get_middleware":
            result = await query_tools.get_middleware(protocol=args.get('protocol','http'),
                                                      name=args.get('name', None))

        elif name == "get_service":
            result = await query_tools.get_service(protocol=args.get('protocol','http'),
                                                      name=args.get('name', None))

        elif name == "get_router":
            result = await query_tools.get_router(protocol=args.get('protocol','http'),
                                                      name=args.get('name', None))

        else:
            raise ValueError(f"Unknown tool: {name}")

        return CallToolResult(content=result)

    except Exception as e:
        logger.exception("Error executing tool %s", name)

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )
            ],
            isError=True
        )


# Initialize MCP server
server = Server(
    "traefik-mcp",
    on_list_tools=list_tools,
    on_call_tool=call_tool,
)


# ---------------------------------------------------------
# Traefik client initialization
# ---------------------------------------------------------

async def initialize_client() -> None:
    """Initialize Traefik client from environment variables."""

    global traefik_client, query_tools

    api_url = os.getenv("TRAEFIK_API_URL")

    if not api_url:
        raise ValueError(
            "TRAEFIK_API_URL environment variable is required"
        )
    api_url = api_url.strip(' "\'')
    
    api_key = os.getenv("TRAEFIK_API_KEY")
    if api_key: api_key = api_key.strip(' "\'')
    
    basic_auth_username = os.getenv("TRAEFIK_BASIC_AUTH_USERNAME")
    if basic_auth_username: basic_auth_username = basic_auth_username.strip(' "\'')
    
    basic_auth_password = os.getenv("TRAEFIK_BASIC_AUTH_PASSWORD")
    if basic_auth_password: basic_auth_password = basic_auth_password.strip(' "\'')

    timeout = float(os.getenv("MCP_TIMEOUT", "30.0"))

    logger.info("Initializing Traefik client for %s", api_url)

    if api_key:
        logger.info("Using API key authentication")

        traefik_client = TraefikClient(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout
        )

    elif basic_auth_username and basic_auth_password:
        logger.info("Using basic authentication")

        traefik_client = TraefikClient(
            api_url=api_url,
            basic_auth_username=basic_auth_username,
            basic_auth_password=basic_auth_password,
            timeout=timeout
        )

    else:
        logger.info("No authentication configured")

        traefik_client = TraefikClient(
            api_url=api_url,
            timeout=timeout
        )

    query_tools = QueryTools(traefik_client)

    if await traefik_client.health_check():
        logger.info("Successfully connected to Traefik API")
    else:
        logger.warning(
            "Failed to connect to Traefik API - "
            "server will start but tools may fail"
        )


# ---------------------------------------------------------
# Starlette SSE application
# ---------------------------------------------------------

def create_starlette_app() -> Starlette:

    sse_path = os.getenv("MCP_SSE_PATH", "/mcp/sse").lower().strip(' "\'')
    message_path = os.getenv("MCP_MESSAGE_PATH", "/mcp/message").lower().strip(' "\'')

    logger.info(
        "Running in HTTP/SSE mode (SSE: %s, Message: %s)",
        sse_path,
        message_path
    )

    sse_transport = mcp.server.sse.SseServerTransport(
        endpoint=message_path,
        security_settings=None
    )

    async def handle_root(request):
        return JSONResponse({
            "service": "Traefik MCP Server",
            "sse_endpoint": sse_path,
            "message_endpoint": message_path,
        })

    async def handle_sse_starlette(request):

        try:
            async with sse_transport.connect_sse(
                request.scope,
                request.receive,
                request._send
            ) as (read_stream, write_stream):

                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )

        except Exception:
            logger.exception("SSE handler error")

            return JSONResponse(
                status_code=500,
                content={"error": "MCP SSE connection failed"}
            )

    routes = [
        Route(
            "/",
            endpoint=handle_root,
            methods=["GET"],
            name="root"
        ),
        Route(
            sse_path,
            endpoint=handle_sse_starlette,
            methods=["GET"],
            name="sse"
        ),
        Mount(
            message_path,
            app=sse_transport.handle_post_message,
            name="messages"
        ),
    ]

    return Starlette(routes=routes)


# ---------------------------------------------------------
# Main entry point
# ---------------------------------------------------------

async def main() -> None:
    """Main entry point for the server."""

    try:
        logger.info("Starting Traefik MCP server")

        await initialize_client()

        transport_mode = os.getenv(
            "MCP_TRANSPORT",
            "stdio"
        ).lower().strip(' "\'')

        if transport_mode == "stdio":

            logger.info("Starting MCP server using STDIO transport")

            async with mcp.server.stdio.stdio_server() as (
                read_stream,
                write_stream
            ):

                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )

        elif transport_mode in ("http", "sse"):

            host = os.getenv("MCP_HOST", "0.0.0.0")
            port = int(os.getenv("MCP_PORT", "8080"))

            logger.info(
                "Starting HTTP/SSE server on %s:%s",
                host,
                port
            )

            starlette_app = create_starlette_app()

            config = uvicorn.Config(
                app=starlette_app,
                host=host,
                port=port,
                access_log=True
            )

            uv_server = uvicorn.Server(config)

            await uv_server.serve()

        else:
            raise ValueError(
                f"Unknown transport mode '{transport_mode}', "
                "must be 'stdio', 'http' or 'sse'."
            )

    except Exception:
        logger.exception("Failed to start server")
        raise


# ---------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------

def cli_main() -> None:
    """CLI entry point that handles async main."""

    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
