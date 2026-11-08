"""
Traefik Query Tools

MCP tools for querying Traefik configuration and status.
"""
import logging
from typing import Any, Dict, List, Optional
import json

from mcp.types import TextContent
from ..traefik.api_client import TraefikClient, TraefikError
from ..traefik.models import Router, Service, Middleware, TraefikOverview

logger = logging.getLogger(__name__)

def format_overview(overview: TraefikOverview) -> str:
    """Format overview for display."""
    output = ["## Traefik Overview\n"]

    output.append("### Components definition")
    output.append("- **Protocols**: 'http', 'udp', 'tcp'")
    output.append("- **Type**: 'middlewares', 'routers', 'services'")
    output.append("")

    
    output.append("### Summary")
    output.append(f"- **Total Routers**: {overview.total_routers}")
    output.append(f"- **Total Services**: {overview.total_services}")
    output.append(f"- **Total Middlewares**: {overview.total_middlewares}")
    output.append("")
    
    if overview.router:
        output.append("### Routers by protocol")
        for provider, count in overview.router.items():
            output.append(f"- **{provider}**: {count}")
        output.append("")
    
    if overview.service:
        output.append("### Services by protocol")
        for provider, count in overview.service.items():
            output.append(f"- **{provider}**: {count}")
        output.append("")
    
    if overview.middleware:
        output.append("### Middlewares by protocol")
        for provider, count in overview.middleware.items():
            output.append(f"- **{provider}**: {count}")
        output.append("")
    
    if overview.features:
        output.append("### Features")
        for feature, value in overview.features.items():
            output.append(f"- **{feature}**: {value}")
        output.append("")

    if overview.providers:
        output.append("### Providers")
        for provider in overview.providers:
            output.append(f"- **{provider}**")
        output.append("")
        
    return "\n".join(output)

def format_version(version: dict) -> str:
    output = ["## Traefik version"]
    output.append(f"- **Version** : {version['Version']}")
    output.append(f"- **Codename** : {version['Codename']}")
    output.append(f"- **startDate** : {version['startDate']}")
    return "\n".join(output)

def format_generic(
    data: Any, 
    title: str = "", 
    indent: int = 2,
    use_tables: bool = True
) -> str:
    """
    Convertit un objet JSON ou une liste en Markdown formaté.
    
    Args:
        data: Données JSON (dict, list, object primitive)
        title: Titre optionnel pour le bloc Markdown
        indent: Tabulation des tableaux et objets (défaut 2)
        use_tables: Utiliser des tableaux si c'est une dict à liste de tuples (défaut True)
    
    Returns:
        String Markdown formaté
    """
    md = []
    
    # Titre du bloc (si fourni)
    if title:
        if isinstance(data, str):
            title_md = f"**{title}**"
        else:
            title_md = f"\n\n### {title}"
        md.append(title_md)
    
    # Traitement récursif selon le type de données
    if data is None:
        return ""
    
    elif isinstance(data, str):
        # Chaîne : formatage basique
        try:
            json_data = json.loads(data)
            result = _format_generic_recursive(json_data, indent=indent, use_tables=use_tables)
            return result if title == "" else title_md + "\n" + result
        except json.JSONDecodeError:
            if title:
                md.append(f"- **{title}**: `{data}`")
            else:
                md.append(f"{data}")
            return "\n".join(md)
    
    elif isinstance(data, (dict, list)):
        # Inclure le titre dans le résultat
        formatted = _format_generic_recursive(data, indent=indent, use_tables=use_tables)
        return title_md + "\n" + formatted if title else formatted
    
    else:
        # Primitive: string, int, float, bool
        if isinstance(data, bool):
            md.append(f"- `{data}`")
        elif isinstance(data, int):
            md.append(f"- `{data}`")
        elif isinstance(data, float):
            md.append(f"- `{data:.2f}`")
        else:
            md.append(f"- `{str(data)}`")
        return "\n".join(md)

def _format_generic_recursive(
    data: Any, 
    indent: int = 2,
    use_tables: bool = True
) -> str:
    """Recurssive formatter pour les structures JSON complexes"""
    
    # Cas vide/null
    if data is None or data == "":
        return "- `null`"
    
    # Liste
    elif isinstance(data, list):
        result = []
        
        if len(data) == 0:
            return ""
        
        for item in data:
            if isinstance(item, list) or isinstance(item, dict):
                result.append(f"- {format_generic(item)}")
            elif isinstance(item, bool):
                result.append(f"- `{str(item).lower()}`")
            else:
                result.append(f"- `{str(item)}`")
        
        return "\n".join(result) if use_tables else json.dumps(data, indent=indent)
    
    # Dictionnaire (ou objet JSON)
    elif isinstance(data, dict):
        result = []
        
        # Titre principal si présent
        for key in data:
            value = data[key]
            # Gérer les clés spéciales comme "name" ou "rule"
            if key == "name":
                result.append(f"- **`{value}`** (Provider: `{data.get('provider', 'N/A')}`)")
            elif key == "rule" or key == "status":
                result.append(f"- {key.capitalize()}: `{value}`")
            else:
                result.append(f"- {key}: {format_generic(value)}")
        
        return "\n".join(result) if use_tables else json.dumps(data, indent=indent)
    
    # Chaîne (déjà gérée par les appels récursifs)
    elif isinstance(data, str):
        return f"`{data}`"


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
            overview = TraefikOverview(**overview_data)
            formatted = format_overview(overview)
            
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
            version = await self.client.get_version()
            formatted = format_version(version)
            
            return [TextContent(type="text", text=formatted)]
            
        except TraefikError as e:
            error_msg = f"Failed to get version: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def get_api_content(self, endpoint: str) -> List[TextContent]:
        """
        Get the content of api endpoint
        
        Args:
            endpoint : API endpoint, e.g. '/api/http/routers'
            
        Returns:
            Formatted content
        """
        try:
            raw_data = await self.client.get_api_content(endpoint)
            title = " ".join(endpoint.split("/")[2:])
            formatted = format_generic(raw_data,title=title )
            
            return [TextContent(type="text", text=formatted)]
            
        except TraefikError as e:
            error_msg = f"Failed to access {endpoint}: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

