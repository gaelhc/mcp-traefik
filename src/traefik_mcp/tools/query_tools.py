"""
Traefik Query Tools

MCP tools for querying Traefik configuration and status.
"""
import logging
from typing import List

from mcp.types import TextContent
from ..traefik.api_client import TraefikClient, TraefikError
from ..traefik.models import Overview, Version
from ..traefik.models import Router, Service, Middleware, EntryPoint
from ..traefik.models import ProtocolType

logger = logging.getLogger(__name__)

class Formatter:

    @classmethod
    def format_overview(cls,overview: Overview) -> str:
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
    def format_version(cls,version: Version) -> str:
        output = ["# Traefik version"]
        output.append(f"- **Version** : {version.version}")
        output.append(f"- **Codename** : {version.codename}")
        output.append(f"- **startDate** : {version.startdate}")
        
        output.append("")
        return "\n".join(output)

    @classmethod
    def format_entrypoint(cls,entrypoint: EntryPoint, short: bool = False) -> str:
        output = [f"## Entrypoint : {entrypoint.name}"]

        output.append(f"- **address**: {entrypoint.address}")
        if short: 
            return "\n".join(output)

        output.append(f"### Details")
        output.append(f"- **http**: {entrypoint.http}")
        output.append(f"- **transport**: ")
        output.append(f"    - **life cyle**: {entrypoint.transport.get("lifeCycle","N/A")}")
        output.append(f"    - **responding timeouts**: {entrypoint.transport.get("respondingTimeouts","N/A")}")
        output.append(f"- **forwarded headers**: {entrypoint.forwardedHeaders}")
    
        output.append("")
        return "\n".join(output)

    @classmethod
    def format_middleware(cls,middleware: Middleware, short: bool = False) -> str:
        output = [f"## Middleware : {middleware.name}"]

        output.append(f"- **protocol**: {middleware.protocol}")
        output.append(f"- **provider**: {middleware.provider}")
        output.append(f"- **type**: {middleware.type}")
        output.append(f"- **status**: {middleware.status}")
        if len(middleware.usedBy) <= 0:
            output.append(f"- **not used**")
        else:
            output.append(f"- **used by**: \n{"\n".join(f"\t- {item}" for item in middleware.usedBy)}")
        
        output.append("")
        if short: 
            return "\n".join(output)

        output.append(f"### Details")
        output.append(f"\n".join(f"- **{k}**: {str(v)}" for k, v in middleware.details.items()))
        output.append("")

        return "\n".join(output)

    @classmethod    
    def format_service(cls,service: Service, short: bool = False) -> str:
        output = [f"## Service : {service.name}"]

        output.append(f"- **protocol**: {service.protocol}")
        output.append(f"- **provider**: {service.provider}")
        output.append(f"- **status**: {service.status}")
        output.append(f"- **type**: {service.type}")
        if len(service.serverStatus) > 0:
            output.append(f"- **server status**: \n{"\n".join(f"\t- {item}" for item in service.serverStatus)}")
        output.append("")

        if short:
            return "\n".join(output)

        output.append(f"### Details")
        output.append(f"\n".join(f"- **{k}**: {v}" for k, v in service.details.items()))
        output.append("")

        return "\n".join(output)

    @classmethod
    def format_router(cls,router: Router, short: bool = False) -> str:
        output = [f"## Router : {router.name}"]

        output.append(f"- **protocol**: {router.protocol}")
        output.append(f"- **provider**: {router.provider}")
        output.append(f"- **rule**: {router.rule}")
        output.append(f"- **service**: {router.service}")
        output.append(f"- **status**: {router.status}")
        if router.entryPoints:
            output.append(f"- **entrypoints**:")
            output.append(f"{"\n".join(f"\t- {item}" for item in router.entryPoints)}")
        if router.middlewares:
            output.append(f"- **middlewares**:")
            output.append(f"{"\n".join(f"\t- {item}" for item in router.middlewares)}")

        output.append("")
        
        if short:
            return "\n".join(output)

        output.append(f"### Details")
        output.append(f"- **tls**: {router.tls}")
        output.append(f"- **priority**: {router.priority}")
        output.append(f"- **observability**: {router.observability}")
        if router.using:
            output.append(f"- **using**:")
            output.append(f"{"\n".join(f"\t- {item}" for item in router.using)}")
        
        output.append("")

        return "\n".join(output)


class QueryTools:
    """Container for Traefik query tools."""
    
    def __init__(self, client: TraefikClient):
        """Initialize query tools with Traefik client."""
        self.client = client
       
    async def get_overview(self) -> List[TextContent]:
        """
        Get complete Traefik status overview.
        
        Returns:
            Formatted overview information
        """
        try:
            overview_data = await self.client.get_overview()
            overview = Overview(**overview_data)
            formatted = Formatter.format_overview(overview)
            
            return [TextContent(type="text", text=formatted)]
            
        except TraefikError as e:
            error_msg = f"Failed to get overview: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def get_version(self) -> List[TextContent]:
        """
        Get Traefik API version.
        
        Returns:
            Formatted overview information
        """
        try:
            raw_json = await self.client.get_version()
            version = Version(**raw_json)
            formatted = Formatter.format_version(version)
            
            return [TextContent(type="text", text=formatted)]
            
        except TraefikError as e:
            error_msg = f"Failed to get version: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def get_entrypoint(self, 
                             name: str | None) -> List[TextContent]:
        """
        Get the content of api endpoint
        
        Args:
            endpoint : API endpoint, e.g. '/api/http/routers'
            
        Returns:
            Formatted content
        """
        try:
            endpoint = "/api/entrypoints"
            if name: endpoint = f"{endpoint}/{name}"
            raw_data = await self.client.get_api_content(endpoint)
            formatted = ["# Entrypoints\n"]
            short_format = True
            if name:
                raw_data = [raw_data]
                short_format = False
            for data in raw_data:
                entrypoint = EntryPoint(**data)
                formatted.append(Formatter.format_entrypoint(entrypoint, short=short_format))   
            return [TextContent(type="text", text="\n".join(formatted))]
            
        except TraefikError as e:
            error_msg = f"Failed to access {endpoint}: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def get_middleware(self, 
                             protocol: ProtocolType,
                             name: str | None) -> List[TextContent]:
        """
        Get the content of api endpoint
        
        Args:
            endpoint : API endpoint, e.g. '/api/http/routers'
            
        Returns:
            Formatted content
        """
        try:
            endpoint = f"/api/{protocol}/middlewares"
            if name: endpoint = f"{endpoint}/{name}"
            raw_data = await self.client.get_api_content(endpoint)
            formatted = ["# Middlewares\n"]
            short_format = True
            if name:
                raw_data = [raw_data]
                short_format = False
            for data in raw_data:
                data = Middleware.parseData(protocol, data)
                middleware = Middleware(**data)
                formatted.append(Formatter.format_middleware(middleware, short=short_format))   
            return [TextContent(type="text", text="\n".join(formatted))]
            
        except TraefikError as e:
            error_msg = f"Failed to access {endpoint}: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def get_service(self, 
                             protocol: ProtocolType,
                             name: str | None) -> List[TextContent]:
        """
        Get the content of api endpoint
        
        Args:
            endpoint : API endpoint, e.g. '/api/http/routers'
            
        Returns:
            Formatted content
        """
        try:
            endpoint = f"/api/{protocol}/services"
            if name: endpoint = f"{endpoint}/{name}"
            raw_data = await self.client.get_api_content(endpoint)
            formatted = ["# Services\n"]
            short_format = True
            if name:
                raw_data = [raw_data]
                short_format = False
            for data in raw_data:
                data = Service.parseData(protocol, data)
                service = Service(**data)
                formatted.append(Formatter.format_service(service, short=short_format))   
            return [TextContent(type="text", text="\n".join(formatted))]
            
        except TraefikError as e:
            error_msg = f"Failed to access {endpoint}: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def get_router(self, 
                             protocol: ProtocolType,
                             name: str | None) -> List[TextContent]:
        """
        Get the content of api endpoint
        
        Args:
            endpoint : API endpoint, e.g. '/api/http/routers'
            
        Returns:
            Formatted content
        """
        try:
            endpoint = f"/api/{protocol}/routers"
            if name: endpoint = f"{endpoint}/{name}"
            raw_data = await self.client.get_api_content(endpoint)
            formatted = ["# Routers\n"]
            short_format = True
            if name:
                raw_data = [raw_data]
                short_format = False
            for data in raw_data:
                data = Router.parseData(protocol, data)
                router = Router(**data)
                formatted.append(Formatter.format_router(router, short=short_format))   
            return [TextContent(type="text", text="\n".join(formatted))]
            
        except TraefikError as e:
            error_msg = f"Failed to access {endpoint}: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
