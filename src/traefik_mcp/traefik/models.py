"""
Traefik Data Models

Pydantic models for Traefik entities with validation and serialization.
"""
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

ProtocolType = Literal['http', 'tcp', 'udp']

class TraefikModel(BaseModel):
    """Base model for all Traefik entities."""
    
    model_config = ConfigDict(extra='allow')  # Allow additional fields from Traefik API


class Router(TraefikModel):
    """Traefik HTTP Router model."""
    
    name: str
    protocol: ProtocolType
    provider: str
    rule: str
    status: str
    entryPoints: List[str]
    tls: Optional[dict] = None
    middlewares: Optional[List[str]] = None
    service: Optional[str] = None
    observability: Optional[Dict] = None 
    priority: Optional[int] = None
    using: List[str] = None
    
    @classmethod
    def parseData(cls, protocol, data: dict[str, Any]) -> dict[str, Any]:
        data["protocol"] = protocol
        return data


class Service(TraefikModel):
    """Traefik HTTP Service model."""
    
    name: str
    protocol: ProtocolType
    provider: str
    status: str
    type: Optional[str] = None
    serverStatus: Optional[Dict[str, Any]] = []
    details: dict[str, Any] = {}
    
    @classmethod
    def parseData(cls, protocol, data: dict[str, Any]) -> dict[str, Any]:
        data["protocol"] = protocol
        data["details"] = Service._getDetails(data)
        return data
    def _getDetails(data:dict[str, Any]) -> dict[str, Any]:
        if "type" in data :
            service_type = data["type"].lower()
            for k, v in data.items():
                if k.lower() == service_type:
                    return v
        return {}


class Middleware(TraefikModel):
    """Traefik HTTP Middleware model."""
    
    name: str
    protocol: ProtocolType
    provider: str
    type: str
    usedBy: Optional[List[str]] = []
    status: str
    details: dict

    @classmethod
    def parseData(cls, protocol, data: dict[str, Any]) -> dict[str, Any]:
        data["protocol"] = protocol
        data["details"] = Middleware._getDetails(data)
        return data
    def _getDetails(data:dict[str, Any]) -> dict[str, Any]:
        middleware_type = data["type"].lower()
        for k, v in data.items():
            if k.lower() == middleware_type:
                return v
        if 'plugin' in data:
            return data["plugin"]
        return {middleware_type: "N/A"}


class EntryPoint(TraefikModel):
    """Traefik EntryPoint model."""
    
    name: str
    address: str
    http: Optional[Dict[str, Any]] = None
    transport: Optional[Dict[str, Any]] = None
    forwardedHeaders: Optional[Dict[str, Any]] = None

    @classmethod
    def parseData(cls, data: dict[str, Any]) -> dict[str, Any]:
        return data

class Overview(TraefikModel):
    """Traefik overview information."""
    
    http: Dict[str, Any] = Field(default_factory=dict)
    tcp: Dict[str, Any] = Field(default_factory=dict)
    udp: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)
    providers: List[str] = Field(default_factory=list)
    
    @property
    def total_routers(self) -> int:
        """Total number of routers."""
        return (self.http.get('routers', {}).get('total', 0) + 
                self.tcp.get('routers', {}).get('total', 0) + 
                self.udp.get('routers', {}).get('total', 0))
    
    @property
    def total_services(self) -> int:
        """Total number of services."""
        return (self.http.get('services', {}).get('total', 0) + 
                self.tcp.get('services', {}).get('total', 0) + 
                self.udp.get('services', {}).get('total', 0))
    
    @property
    def total_middlewares(self) -> int:
        """Total number of middlewares."""
        return (self.http.get('middlewares', {}).get('total', 0) + 
                self.tcp.get('middlewares', {}).get('total', 0) + 
                self.udp.get('middlewares', {}).get('total', 0))
    
    @property
    def router(self) -> Dict[str, int]:
        """Router counts by protocol."""
        return {
            'http': self.http.get('routers', {}).get('total', 0),
            'tcp': self.tcp.get('routers', {}).get('total', 0),
            'udp': self.udp.get('routers', {}).get('total', 0)
        }
    
    @property
    def service(self) -> Dict[str, int]:
        """Service counts by protocol."""
        return {
            'http': self.http.get('services', {}).get('total', 0),
            'tcp': self.tcp.get('services', {}).get('total', 0),
            'udp': self.udp.get('services', {}).get('total', 0)
        }
    
    @property
    def middleware(self) -> Dict[str, int]:
        """Middleware counts by protocol."""
        return {
            'http': self.http.get('middlewares', {}).get('total', 0),
            'tcp': self.tcp.get('middlewares', {}).get('total', 0),
            'udp': self.udp.get('middlewares', {}).get('total', 0)
        }


class Version(TraefikModel):
    """Traefik version information."""
    
    version: str = Field(alias="Version")
    codename: str = Field(alias="Codename")
    startdate: str = Field(alias="startDate")


class HealthStatus(TraefikModel):
    """Health status information."""
    
    healthy: bool
    message: Optional[str] = None
    version: Optional[str] = None
    uptime: Optional[str] = None


