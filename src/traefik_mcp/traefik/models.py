"""
Traefik Data Models

Pydantic models for Traefik entities with validation and serialization.
"""
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

ProtocolType = Literal['http', 'tcp', 'udp']

class Models:
    class TraefikModel(BaseModel):
        """Base model for all Traefik entities."""
        
        model_config = ConfigDict(extra='allow')  # Allow additional fields from Traefik API


    class Router(BaseModel):
        """Traefik HTTP Router standard model."""
        model_config = ConfigDict(extra='ignore')  # Limit fields to standard model
        
        name: str
        provider: str
        protocol: ProtocolType
        status: str

        @classmethod
        def parseData(cls, protocol: str, data: Dict[str, Any]) -> Dict[str, Any]:
            """Parse router data from API response."""
            data["protocol"] = protocol
            return data

    class RouterDetails(Router):
        """Traefik HTTP Router detailed model."""
        model_config = ConfigDict(extra='allow')  # Keep all unexpected fields
        rule: str
        entryPoints: List[str]
        tls: Optional[Dict[str, Any]] = None
        middlewares: Optional[List[str]] = None
        service: Optional[str] = None
        observability: Optional[Dict[str, Any]] = None
        priority: Optional[int] = None
        using: Optional[List[str]] = None
        


    class Service(BaseModel):
        """Traefik HTTP Service standard model."""
        model_config = ConfigDict(extra='ignore')  # Limit fields to standard model
        
        name: str
        protocol: ProtocolType
        provider: str
        status: str
        type: Optional[str] = None

        @classmethod
        def parseData(cls, protocol: str, data: Dict[str, Any]) -> Dict[str, Any]:
            """Parse service data from API response."""
            data["protocol"] = protocol
            data["details"] = Models.Service._getDetails(data)
            return data

        @classmethod
        def _getDetails(cls, data: Dict[str, Any]) -> Dict[str, Any]:
            """Extract type-specific details from service data."""
            if "type" not in data:
                return {}
            
            service_type = data["type"].lower()
            for k, v in data.items():
                if k.lower() == service_type:
                    return v
            return {}

    class ServiceDetails(Service):
        """Traefik HTTP Service detailed model."""
        model_config = ConfigDict(extra='allow')  # Keep all unexpected fields

        serverStatus: Optional[Dict[str, Any]] = {}
        details: dict[str, Any] = {}
        


    class Middleware(BaseModel):
        """Traefik HTTP Middleware standard model."""
        model_config = ConfigDict(extra='ignore')  # Limit fields to standard model
        
        name: str
        protocol: ProtocolType
        provider: str
        type: str
        status: str

        @classmethod
        def parseData(cls, protocol: str, data: Dict[str, Any]) -> Dict[str, Any]:
            """Parse middleware data from API response."""
            data["protocol"] = protocol
            data["details"] = Models.Middleware._getDetails(data)
            return data

        @classmethod
        def _getDetails(cls, data: Dict[str, Any]) -> Dict[str, Any]:
            """Extract type-specific details from middleware data."""
            if "type" not in data:
                return {}
            
            middleware_type = data["type"].lower()
            for k, v in data.items():
                if k.lower() == middleware_type:
                    return v
            
            if "plugin" in data:
                return data["plugin"]
            
            return {middleware_type: "N/A"}

    class MiddlewareDetails(Middleware):
        """Traefik HTTP Middleware detailed model."""
        model_config = ConfigDict(extra='allow')  # Allow additional fields from Traefik API

        usedBy: Optional[List[str]] = None
        details: Dict[str, Any] = Field(default_factory=dict)


    class EntryPoint(BaseModel):
        """Traefik EntryPoint standard model."""
        
        name: str
        address: str
       
        @classmethod
        def parseData(cls, data: Dict[str, Any]) -> Dict[str, Any]:
            """Parse entrypoint data from API response."""
            return data

    class EntryPointDetails(EntryPoint):
        """Traefik EntryPoint detailed model."""

        http: Optional[Dict[str, Any]] = None
        transport: Optional[Dict[str, Any]] = None
        forwardedHeaders: Optional[Dict[str, Any]] = None

    class Overview(TraefikModel):
        """Traefik overview information."""
        
        http: Dict[str, Any] = Field(default_factory=dict)
        tcp: Dict[str, Any] = Field(default_factory=dict)
        udp: Dict[str, Any] = Field(default_factory=dict)
        features: Dict[str, Any] = Field(default_factory=dict)
        providers: List[str] = Field(default_factory=list)
        
        @property
        def total_routers(self) -> int:
            """Total number of routers across all protocols."""
            return (self.http.get('routers', {}).get('total', 0) + 
                    self.tcp.get('routers', {}).get('total', 0) + 
                    self.udp.get('routers', {}).get('total', 0))
        
        @property
        def total_services(self) -> int:
            """Total number of services across all protocols."""
            return (self.http.get('services', {}).get('total', 0) + 
                    self.tcp.get('services', {}).get('total', 0) + 
                    self.udp.get('services', {}).get('total', 0))
        
        @property
        def total_middlewares(self) -> int:
            """Total number of middlewares across all protocols."""
            return (self.http.get('middlewares', {}).get('total', 0) + 
                    self.tcp.get('middlewares', {}).get('total', 0) + 
                    self.udp.get('middlewares', {}).get('total', 0))
        
        @property
        def router(self) -> Dict[str, int]:
            """Router counts grouped by protocol."""
            return {
                'http': self.http.get('routers', {}).get('total', 0),
                'tcp': self.tcp.get('routers', {}).get('total', 0),
                'udp': self.udp.get('routers', {}).get('total', 0)
            }
        
        @property
        def service(self) -> Dict[str, int]:
            """Service counts grouped by protocol."""
            return {
                'http': self.http.get('services', {}).get('total', 0),
                'tcp': self.tcp.get('services', {}).get('total', 0),
                'udp': self.udp.get('services', {}).get('total', 0)
            }
        
        @property
        def middleware(self) -> Dict[str, int]:
            """Middleware counts grouped by protocol."""
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


    class AccessEntry(BaseModel):
        model_config = ConfigDict(extra='allow')  # Allow additional fields from Traefik API
