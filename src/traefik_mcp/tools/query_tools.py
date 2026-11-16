"""
Traefik Query Tools

MCP tools for querying Traefik configuration and status.
"""
import logging
from typing import List

from mcp.types import TextContent
from traefik_mcp.traefik.api_client import TraefikClient, TraefikError
from traefik_mcp.traefik import Models, ProtocolType

logger = logging.getLogger(__name__)

class Formatter:

    @classmethod
    def format_overview(cls,overview: Models.Overview) -> str:
        """Format overview for display."""
        output = ["# Traefik Overview\n"]

        output.append("## Traefik-MCP usage")
        output.append("- **Protocols**: 'http', 'udp', 'tcp'")
        output.append("- **Entrypoints**:")
        output.append("\t- get_entrypoint(): returns list of entrypoints")
        output.append("\t- get_entrypoint(router_name): returns details about a entrypoint")
        output.append("- **Routers**:")
        output.append("\t- get_router(protocol): returns list of routers")
        output.append("\t- get_router(protocol,router_name): returns details about a router")
        output.append("- **Middlewares**:")
        output.append("\t- get_middleware(protocol): returns list of middlewares")
        output.append("\t- get_middleware(protocol,router_name): returns details about a middleware")
        output.append("- **Services**:")
        output.append("\t- get_service(protocol): returns list of services")
        output.append("\t- get_service(protocol,router_name): returns details about a service")
        output.append("")
        output.append("**NEVER REQUEST FOR DETAILS ABOUT A COMPONENT BEFORE REQUESTING FOR A LIST OF COMPONENTS")
        output.append("")
        
        output.append("## Summary")
        output.append(f"- **Total Routers**: {overview.total_routers}")
        output.append(f"- **Total Services**: {overview.total_services}")
        output.append(f"- **Total Middlewares**: {overview.total_middlewares}")
        output.append("")
        
        if overview.router:
            output.append("## Routers by protocol")
            for provider, count in overview.router.items():
                output.append(f"- **{provider}**: {count}")
            output.append("")
        
        if overview.service:
            output.append("## Services by protocol")
            for provider, count in overview.service.items():
                output.append(f"- **{provider}**: {count}")
            output.append("")
        
        if overview.middleware:
            output.append("## Middlewares by protocol")
            for provider, count in overview.middleware.items():
                output.append(f"- **{provider}**: {count}")
            output.append("")
        
        if overview.features:
            output.append("## Features")
            for feature, value in overview.features.items():
                output.append(f"- **{feature}**: {value}")
            output.append("")

        if overview.providers:
            output.append("## Providers")
            for provider in overview.providers:
                output.append(f"- **{provider}**")
            output.append("")

        output.append("")
        
        return "\n".join(output)

    @classmethod
    def format_version(cls, version: Models.Version) -> str:
        """Format version info for display."""
        output = ["# Traefik version"]
        output.append(f"- **Version**: {version.version}")
        output.append(f"- **Codename**: {version.codename}")
        output.append(f"- **Start Date**: {version.startdate}")
        output.append("")
        return "\n".join(output)

    @classmethod
    def format_entrypoint(cls, entrypoint: Models.EntryPoint | Models.EntryPointDetails) -> str:
        output = [f"## Entrypoint: {entrypoint.name}"]
        output.append(f"- **address**: {entrypoint.address}")
        
        # Check si c'est un objet détaillé
        if not isinstance(entrypoint, Models.EntryPointDetails):
            output.append("")
            return "\n".join(output)

        output.append(f"- **http**: {entrypoint.http}")
        output.append(f"- **transport**: ")
        output.append(f"    - **life cyle**: {entrypoint.transport.get("lifeCycle","N/A")}")
        output.append(f"    - **responding timeouts**: {entrypoint.transport.get("respondingTimeouts","N/A")}")
        output.append(f"- **forwarded headers**: {entrypoint.forwardedHeaders}")
    
        output.append("")
        return "\n".join(output)

    @classmethod
    def format_middleware(cls, middleware: Models.Middleware | Models.MiddlewareDetails) -> str:
        """Format a middleware for display."""
        output = [f"## Middleware: {middleware.name}"]

        output.append(f"- **protocol**: {middleware.protocol}")
        output.append(f"- **provider**: {middleware.provider}")
        output.append(f"- **type**: {middleware.type}")
        output.append(f"- **status**: {middleware.status}")

        if not isinstance(middleware, Models.MiddlewareDetails):
            output.append("")
            return "\n".join(output)

        if middleware.usedBy:
            output.append(f"- **used by**:")
            lines = ["\t- " + item for item in middleware.usedBy]
            output.extend(lines)
        else:
            output.append(f"- **not used**")

        details = middleware.details or {}
        for k, v in details.items():
            output.append(f"- **{k}**: {str(v)}")

        output.append("")
        return "\n".join(output)

    @classmethod
    def format_service(cls, service: Models.Service | Models.ServiceDetails) -> str:
        """Format a service for display."""
        output = [f"## Service: {service.name}"]

        output.append(f"- **protocol**: {service.protocol}")
        output.append(f"- **provider**: {service.provider}")
        output.append(f"- **status**: {service.status}")
        output.append(f"- **type**: {service.type}")

        if not isinstance(service, Models.ServiceDetails):
            output.append("")
            return "\n".join(output)

        server_status = service.serverStatus or {}
        if server_status:
            lines = [f"- **server status**:"] + [f"\t- {k}: {str(v)}" for k, v in server_status.items()]
            output.append("\n".join(lines))

        details = service.details or {}
        for k, v in details.items():
            output.append(f"- **{k}**: {str(v)}")

        output.append("")
        return "\n".join(output)

    @classmethod
    def format_router(cls, router: Models.Router | Models.RouterDetails) -> str:
        """Format a router for display."""
        output = [f"## Router: {router.name}"]

        output.append(f"- **protocol**: {router.protocol}")
        output.append(f"- **provider**: {router.provider}")
        output.append(f"- **status**: {router.status}")

        if not isinstance(router, Models.RouterDetails):
            output.append("")
            return "\n".join(output)

        output.append(f"- **rule**: {router.rule}")
        output.append(f"- **service**: {router.service}")

        if router.entryPoints:
            output.append(f"- **entrypoints**:")
            lines = ["\t- " + item for item in router.entryPoints]
            output.extend(lines)

        if router.middlewares:
            output.append(f"- **middlewares**:")
            lines = ["\t- " + item for item in router.middlewares]
            output.extend(lines)

        output.append(f"- **tls**: {router.tls}")
        output.append(f"- **priority**: {router.priority}")
        output.append(f"- **observability**: {router.observability}")

        if router.using:
            output.append(f"- **using**:")
            output.extend("\t " + item for item in router.using)
    
        output.append("")
        return "\n".join(output)
