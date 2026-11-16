"""
Traefik MCP Server

A Model Context Protocol server for managing Traefik reverse proxy instances.
"""
import asyncio
import logging
import os
from pathlib import Path

from fastmcp import FastMCP
from typing import Any, List, Dict, Literal, Optional

from traefik_mcp.traefik.api_client import TraefikClient
from traefik_mcp.traefik import Models
from traefik_mcp.tools.query_tools import Formatter
from traefik_mcp.accesslogs import RequestAccessLog


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Traefik client initialization
# ---------------------------------------------------------
# Global variables
traefik_client: TraefikClient | None = None

# Initialization of Traefik Client
def get_client() -> None:
    """Initialize Traefik client from environment variables."""

    global traefik_client

    if traefik_client is None:
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

        access_log = os.getenv("TRAEFIK_ACCESS_LOG")
        if access_log: 
            access_log = access_log.strip(' "\'')
            if not Path(access_log).is_file():
                logger.error(f"Traefik access.log file not found.\nCheck  TRAEFIK_ACCESS_LOG: {access_log}")
                access_log = None
                
        timeout = float(os.getenv("MCP_TIMEOUT", "30.0"))

        logger.info("Initializing Traefik client for %s", api_url)

        if api_key:
            logger.info("Using API key authentication")

            traefik_client = TraefikClient(
                api_url=api_url,
                api_key=api_key,
                access_log_file=Path(access_log),
                timeout=timeout
            )

        elif basic_auth_username and basic_auth_password:
            logger.info("Using basic authentication")

            traefik_client = TraefikClient(
                api_url=api_url,
                basic_auth_username=basic_auth_username,
                basic_auth_password=basic_auth_password,
                access_log_file=Path(access_log),
                timeout=timeout
            )

        else:
            logger.info("No authentication configured")

            traefik_client = TraefikClient(
                api_url=api_url,
                access_log_file=Path(access_log),
                timeout=timeout
            )

    
    if traefik_client.health_check():
        logger.info("Successfully connected to Traefik API")
    else:
        logger.warning(
            "Failed to connect to Traefik API - "
            "server will start but tools may fail"
        )

    return traefik_client

# ---------------------------------------------------------
# MCP Tool definitions
# ---------------------------------------------------------
mcp = FastMCP("traefik-mcp")

#
# Basic tools
#
@mcp.tool
async def overview(
    output_format: Optional[Literal['markdown', 'structured']] = 'structured'
) -> Dict[str, Any]:
    """
    Get an overview of the Traefik instance configuration.
    
    Arguments:
        output_format: Literal['markdown', 'structured']. Default: 'structured'.
            Specify the output format:
                - markdown: returns a pure Markdown document
                - structured: returns a structured Dict

    Returns:
        A dictionary, containing:
            - "request": a dict summarizing the request and its execution
            - "overview": the results of the request, format is specified by `output_format`

    """
    client:TraefikClient = get_client()
    res = await client.get_overview()

    output = {}
    output['request'] = {
        "tool": "overview",
        "arguments": {
            "output_format": output_format
        },
        "total_items": 1
        }

    overview = Models.Overview(**res)

    if output_format == "structured":
        output["overview"] = overview

    else :
        output["overview"] = Formatter.format_overview(overview)

    return output

@mcp.tool
async def version(
    output_format: Optional[Literal['markdown', 'structured']] = 'structured'
) -> Dict[str, Any]:
    """
    Get the current version of the Traefik instance configuration
    
    Arguments:
        output_format: Literal['markdown','structured']. Default: 'structured'
            Specify the output format:
                - markdown : returns a pure Markdown document
                - structured : returns a strctured Dict

    Returns:
        A dictionnary, containing:
            - "request" : a dict summarizing the request and its execution
            - "version" : the results of the request, format is specified by
                           `output_format` 

    """
    client:TraefikClient = get_client()
    res = await client.get_version()

    output = {}
    output['request'] = {
        "tool": "version",
        "arguments": {
            "output_format": output_format
        },
        "total_items": 1
        }

    version = Models.Version(**res)

    if output_format == "structured":
        output["version"] = version

    else :
        output["version"] = Formatter.format_version(version)

    return output

#
# Entrypoint tools
#
@mcp.tool
async def list_entrypoints(
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get the list of Traefik entrypoints.
    
    Arguments:
        output_format: Literal['markdown','structured']. Default: 'structured'
            Specify the output format:
                - markdown : returns a pure Markdown document
                - structured : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "entrypoints": a list of Dictionnary. One dict per entrypoint,
            each with a few informations about the entrypoint.

    """
    endpoint = "/api/entrypoints"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
    if type(res) != list:
        res = [res]
        
    output = {}
    output['request'] = {
        "tool": "list_entrypoints",
        "arguments": {
            "output_format": output_format
        },
        "total_items": len(res)
        }

    output["entrypoints"] = []
    for e in res:
        entrypoint = Models.EntryPoint(**e)
        if output_format == "structured":
            output["entrypoints"].append(entrypoint)

        else :
            output["entrypoints"] = output["entrypoints"] + Formatter.format_entrypoint(entrypoint)

    return output

@mcp.tool
async def entrypoint_details(
    entrypoint_name: str,
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get all details about a Traefik entrypoint
    
    Arguments:
        entrypoint_name: str.
            - Specify the entrypoint by its full name.
            Consult `list_entrypoints()` to get the full list of entrypoints.
        output_format: Literal['markdown','structured']. Default: 'structured'
            Specify the output format:
                - markdown : returns a pure Markdown document
                - structured : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "entrypoint": the results of the request, format is specified by
                           `output_format` 

    """
    endpoint = f"/api/entrypoints/{entrypoint_name}"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
        
    output = {}
    output['request'] = {
        "tool": "entrypoint_details",
        "arguments": {
            "entrypoint_name": entrypoint_name,
            "output_format": output_format
        },
        "total_items": 1
        }

    entrypoint = Models.EntryPointDetails(**res)
    if output_format == "structured":
        output["entrypoint"] = entrypoint
    else :
        output["entrypoint"] = Formatter.format_entrypoint(entrypoint)

    return output

#
# Router tools
#
@mcp.tool
async def list_routers(
    protocol: Optional[Literal['http', 'tcp', 'udp']] = 'http',
    output_format: Optional[Literal['markdown', 'structured']] = 'structured'
) -> Dict[str, Any]:
    """
    Get the list of Traefik routers.
    
    Arguments:
        protocol: Specify the protocol. Default: 'http'.
        output_format: Specify the output format. Default: 'structured'.
            - 'markdown' : returns a pure Markdown document
            - 'structured' : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "routers": a list of Dictionnary. One dict per router,
            each with a few informations about the router.

    """
    endpoint = f"/api/{protocol}/routers"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
    if type(res) != list:
        res = [res]
        
    output = {}
    output['request'] = {
        "tool": "list_routers",
        "arguments": {
            "protocol": protocol,
            "output_format": output_format
        },
        "total_items": len(res)
        }

    output["routers"] = []
    for r in res:
        router = Models.Router(**Models.Router.parseData(protocol,r))
        if output_format == "structured":
            output["routers"].append(router)
        else :
            output["routers"] = output["routers"] + Formatter.format_router(router)

    return output

@mcp.tool
async def router_details(
    router_name: str,
    protocol: Optional[Literal['http','tcp','udp']] = 'http',
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get all details about a Traefik router
    
    Arguments:
        router_name: str.
            - Specify the router by its full name including its provider,
              e.g.: 'api@internal' or 'authelia@file' 
            Consult `list_routers()` to get the full list of routers.
        protocol: Specify the protocol. Default: 'http'.
        output_format: Literal['markdown','structured']. Default: 'structured'
            Specify the output format:
                - markdown : returns a pure Markdown document
                - structured : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "router": the results of the request, format is specified by
                        `output_format` 

    """
    endpoint = f"/api/{protocol}/routers/{router_name}"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
        
    output = {}
    output['request'] = {
        "tool": "router_details",
        "arguments": {
            "router_name": router_name,
            "protocol": protocol,
            "output_format": output_format
        },
        "total_items": 1
        }

    router = Models.RouterDetails(**Models.Router.parseData(protocol,res))
    if output_format == "structured":
        output["router"] = router
    else :
        output["router"] = Formatter.format_router(router)

    return output

#
# Service tools
#
@mcp.tool
async def list_services(
    protocol: Optional[Literal['http','tcp','udp']] = 'http',
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get the list of Traefik services.
    
    Arguments:
        protocol: Specify the protocol. Default: 'http'.
        output_format: Specify the output format. Default: 'structured'.
            - 'markdown' : returns a pure Markdown document
            - 'structured' : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "services": a list of Dictionnary. One dict per service,
            each with a few informations about the service.

    """
    endpoint = f"/api/{protocol}/services"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
    if type(res) != list:
        res = [res]
        
    output = {}
    output['request'] = {
        "tool": "list_services",
        "arguments": {
            "protocol": protocol,
            "output_format": output_format
        },
        "total_items": len(res)
        }

    output["services"] = []
    for r in res:
        service = Models.Service(**Models.Service.parseData(protocol,r))
        if output_format == "structured":
            output["services"].append(service)
        else :
            output["services"] = output["services"] + Formatter.format_service(service)

    return output

@mcp.tool
async def service_details(
    service_name: str,
    protocol: Optional[Literal['http','tcp','udp']] = 'http',
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get all details about a Traefik service
    
    Arguments:
        service_name: str.
            - Specify the service by its full name including its provider,
              e.g.: 'api@internal' or 'authelia@file' 
            Consult `list_services()` to get the full list of services.
        protocol: Specify the protocol. Default: 'http'.
        output_format: Literal['markdown','structured']. Default: 'structured'
            Specify the output format:
                - markdown : returns a pure Markdown document
                - structured : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "service": the results of the request, format is specified by
                        `output_format` 

    """
    endpoint = f"/api/{protocol}/services/{service_name}"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
        
    output = {}
    output['request'] = {
        "tool": "service_details",
        "arguments": {
            "protocol": protocol,
            "service_name": service_name,
            "output_format": output_format
        },
        "total_items": 1
        }

    service = Models.ServiceDetails(**Models.Service.parseData(protocol,res))
    if output_format == "structured":
        output["service"] = service
    else :
        output["service"] = Formatter.format_service(service)

    return output

#
# Middleware tools
#
@mcp.tool
async def list_middlewares(
    protocol: Optional[Literal['http','tcp','udp']] = 'http',
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get the list of Traefik middlewares.
    
    Arguments:
        protocol: Specify the protocol. Default: 'http'.
        output_format: Specify the output format. Default: 'structured'.
            - 'markdown' : returns a pure Markdown document
            - 'structured' : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "middlewares": a list of Dictionnary. One dict per middleware,
            each with a few informations about the middleware.

    """
    endpoint = f"/api/{protocol}/middlewares"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
    if type(res) != list:
        res = [res]
        
    output = {}
    output['request'] = {
        "tool": "list_middlewares",
        "arguments": {
            "protocol": protocol,
            "output_format": output_format
        },
        "total_items": len(res)
        }

    output["middlewares"] = []
    for r in res:
        middleware = Models.Middleware(**Models.Middleware.parseData(protocol,r))
        if output_format == "structured":
            output["middlewares"].append(middleware)
        else :
            output["middlewares"] = output["middlewares"] + Formatter.format_middleware(middleware)

    return output

@mcp.tool
async def middleware_details(
    middleware_name: str,
    protocol: Optional[Literal['http','tcp','udp']] = 'http',
    output_format: Optional[Literal['markdown','structured']] = 'structured'
    ) -> Dict[str,Any]:
    """
    Get all details about a Traefik middleware
    
    Arguments:
        middleware_name: str.
            - Specify the middleware by its full name including its provider,
              e.g.: 'api@internal' or 'authelia@file' 
            Consult `list_middlewares()` to get the full list of middlewares.
        protocol: Specify the protocol. Default: 'http'.
        output_format: Literal['markdown','structured']. Default: 'structured'
            Specify the output format:
                - markdown : returns a pure Markdown document
                - structured : returns a structured list of Dict

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "middleware": the results of the request, format is specified by
                        `output_format` 

    """
    endpoint = f"/api/{protocol}/middlewares/{middleware_name}"
    client:TraefikClient = get_client()
    res = await client.get_api_content(endpoint)
        
    output = {}
    output['request'] = {
        "tool": "middleware_details",
        "arguments": {
            "middleware_name": middleware_name,
            "protocol": protocol,
            "output_format": output_format
        },
        "total_items": 1
        }

    middleware = Models.MiddlewareDetails(**Models.Middleware.parseData(protocol,res))
    if output_format == "structured":
        output["middleware"] = middleware
    else :
        output["middleware"] = Formatter.format_middleware(middleware)

    return output

#
# Access.log
#
@mcp.tool
async def explore_access_log(
    filters: str,
    page: Optional[int] = 1,
    per_page: Optional[int] = 50,
    sort: Optional[str] = '-time'
    ) -> Dict[str, Any]:
    """
    Get access logs entries as paginated dictionnaries.
    Access to entries is made by filters using AST-based
    safe expression evaluator.
    
    Arguments:
        filters: str. AST-based safe expression used to filter
                 Traefik access log entries
            - All fields of the Traefik dict entry can be used
              (Refer to `List of Traefik keys`) 
            - Operations: '=', '!=', '>', '>=', '<', 
                          '<=', '~' (i.e. match, not regexp) 
            - Logical operations: '&&', '||'
            Examples of filters:
                - "RequestAddr ~ 'cloud' && RequestMethod != 'GET'"
                > returns entries with RequestAddr matching 'cloud'
                and RequestMethod is not 'GET'
                
                - "time > '2026-12-01' && DownstreamStatus >= 300"
                > returns all errors since 1st of december 2026

        page: Optional[int]. The page to be returned. Default: 1
        per_page: Optional[int]. The number of entries per page
                  to be returned. Default: 50
        sort: Optional[str]. The field used to sort data. Default '-time'.
              Usage : '-time' sort by time, from newer to older
                      '+time' sort by time, from older to newer
                      '+DownstreamStatus' sort by status

    Returns:
        A dictionnary, containing:
            - "request": a dict summarizing the request and its execution
            - "access": a list of dict. Each dict is an entry of the 
                        `access.log` matching the specified filters.


    List of Traefik keys:
        `ClientAddr` [string] : Client IP address with port (`IP:Port`)
        `ClientHost` [string] : Client hostname (if resolvable)
        `ClientPort` [string] : Client source port
        `ClientUsername` [string] : Client username (`-` if unauthenticated)
        `RequestMethod` [string] : HTTP method (GET, POST, PUT, DELETE, etc.)
        `RequestPath` [string] : Full request path (`/`, `/api/xxx`, etc.)
        `RequestHost` [string] : Host header received from the client
        `RequestProtocol` [string] : HTTP protocol (HTTP/1.1, HTTP/2.0)
        `RequestScheme` [string] : Transport scheme (`http`, `https`)
        `RequestContentLength` [int] : Size of the content sent by the client (bytes)
        `RequestCount` [int] : Total number of requests (cumulative or session)
        `RetryAttempts` [int] : Retry attempts (0 by default)
        `DownstreamStatus` [int] : HTTP status code returned to the client (200, 401, 502, etc.)
        `DownstreamContentSize` [int] : Size of the content returned by Traefik (bytes)
        `Overhead` [int] : Additional time added by Traefik (µs)
        `OriginStatus` [int] : HTTP status code returned by the backend (0 if no response)
        `OriginDuration` [int] : Processing duration by the backend only (µs), 0 if none
        `OriginContentSize` [int] : Actual content size from the backend (bytes)
        `Duration` [int] : Total processing duration by Traefik including the backend (µs)
        `GzipRatio` [float] : Gzip compression ratio if enabled
        `TLSCipher` [string] : Cipher suite used for encryption (`TLS_AES_128_GCM_SHA256`)
        `TLSVersion` [string] : TLS version used (`1.2`, `1.3`, etc.)
        `TrustForwardHeader` [boolean] : (in middleware, not log) If true, trusts X-Forwarded-* headers
        `RouterName` [string] : Name of the router that handled the request (`router-name@provider`)
        `ServiceName` [string] : Name of the backend service (`service-name@provider`)
        `ServiceAddress` [string] : Backend IP address (`sync-in:80`, etc.)
        `ServiceURL` [string] : Full backend URL (`http://sync-in:80`)
        `entryPointName` [string] : Name of the entrypoint used (`websecure`, `traefik`, etc.)
        `StartLocal` [string] : Timestamp in server local format (with timezone)
        `StartUTC` [string] : Pure UTC timestamp for reproducibility
        `time` [string] : Final request timestamp (`YYYY-MM-DDTHH:MM:SS+XX:XX`)
        `level` [string] : Log level (info, warning, error)
        `msg` [string] : Log message (often empty)
 
    """
    client:TraefikClient = get_client()
    if client.access_log_file is None:
        raise Exception('Traefik access log file path is not defined.')

    if len(filters) == 0:
        raise ValueError("A filter must be defined")

    try:
        res = await RequestAccessLog(access_log_file=client.access_log_file,
                                     filter_expr=filters,
                                     page=page,
                                     per_page=per_page,
                                     sort=sort)
    except Exception as e:
        raise Exception(f"explore_access_log : \n{e}")
    
        
    output = {}
    output['request'] = {
        "tool": "explore_access_log",
        "arguments": {
            "filters": filters,
            "page": page,
            "per_page": per_page,
            "sort": sort
        },
        "total_pages": res["total_pages"],
        "total_items": res["total_items"]
        }

    output["access"] = res["results"]

    return output