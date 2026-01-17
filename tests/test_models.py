"""
Tests for Traefik Data Models
"""
import pytest
from pydantic import ValidationError

from traefik_mcp.traefik.models import (
    Router, Service, Middleware, EntryPoint, 
    TraefikOverview, TraefikVersion, HealthStatus
)


class TestRouter:
    """Test cases for Router model."""
    
    def test_router_creation(self):
        """Test creating a router with valid data."""
        router = Router(
            name="test-router",
            provider="docker",
            rule="Host(`example.com`)",
            service="test-service",
            entryPoints=["web", "secure"]
        )
        
        assert router.name == "test-router"
        assert router.provider == "docker"
        assert router.rule == "Host(`example.com`)"
        assert router.service == "test-service"
        assert router.entryPoints == ["web", "secure"]
    
    def test_router_with_single_entrypoint(self):
        """Test router with single entrypoint as string."""
        router = Router(
            name="test-router",
            provider="docker",
            rule="Host(`example.com`)",
            entryPoints="web"  # String instead of list
        )
        
        assert router.entryPoints == ["web"]
    
    def test_router_with_single_middleware(self):
        """Test router with single middleware as string."""
        router = Router(
            name="test-router",
            provider="docker",
            rule="Host(`example.com`)",
            middlewares="auth"  # String instead of list
        )
        
        assert router.middlewares == ["auth"]
    
    def test_router_with_empty_lists(self):
        """Test router with None or empty lists."""
        router = Router(
            name="test-router",
            provider="docker",
            rule="Host(`example.com`)",
            entryPoints=None,
            middlewares=[]
        )
        
        assert router.entryPoints == []
        assert router.middlewares == []


class TestService:
    """Test cases for Service model."""
    
    def test_service_loadbalancer(self):
        """Test service with load balancer configuration."""
        service = Service(
            name="test-service",
            provider="docker",
            loadBalancer={
                "method": "wrr",
                "servers": [
                    {"url": "http://localhost:8081", "weight": 1},
                    {"url": "http://localhost:8082", "weight": 2}
                ]
            }
        )
        
        assert service.service_type == "loadbalancer"
        assert len(service.servers) == 2
        assert service.servers[0]["url"] == "http://localhost:8081"
    
    def test_service_mirroring(self):
        """Test service with mirroring configuration."""
        service = Service(
            name="test-service",
            provider="docker",
            mirroring={
                "service": "mirror-service",
                "maxBodySize": 1024
            }
        )
        
        assert service.service_type == "mirroring"
        assert len(service.servers) == 0
    
    def test_service_weighted(self):
        """Test service with weighted configuration."""
        service = Service(
            name="test-service",
            provider="docker",
            weighted={
                "services": [
                    {"name": "service1", "weight": 3},
                    {"name": "service2", "weight": 1}
                ]
            }
        )
        
        assert service.service_type == "weighted"
        assert len(service.servers) == 0
    
    def test_service_unknown_type(self):
        """Test service with no known configuration."""
        service = Service(
            name="test-service",
            provider="docker"
        )
        
        assert service.service_type == "unknown"
        assert len(service.servers) == 0


class TestMiddleware:
    """Test cases for Middleware model."""
    
    def test_middleware_with_known_type(self):
        """Test middleware with explicit type."""
        middleware = Middleware(
            name="test-middleware",
            provider="docker",
            middleware_type="addPrefix"
        )
        
        assert middleware.name == "test-middleware"
        assert middleware.middleware_type == "addPrefix"
    
    def test_middleware_type_inference(self):
        """Test middleware type inference from configuration."""
        middleware = Middleware(
            name="test-middleware",
            provider="docker",
            addPrefix={"prefix": "/api"}
        )
        
        assert middleware.middleware_type == "addPrefix"
    
    def test_middleware_unknown_type(self):
        """Test middleware with unknown type."""
        middleware = Middleware(
            name="test-middleware",
            provider="docker"
        )
        
        assert middleware.middleware_type == "unknown"


class TestTraefikOverview:
    """Test cases for TraefikOverview model."""
    
    def test_overview_creation(self):
        """Test creating overview with data."""
        overview = TraefikOverview(
            router={"docker": 5, "file": 2},
            service={"docker": 3},
            middleware={"file": 1},
            entrypoint={"web": 1, "secure": 1}
        )
        
        assert overview.total_routers == 7
        assert overview.total_services == 3
        assert overview.total_middlewares == 1
        assert overview.total_entrypoints == 2
    
    def test_overview_empty(self):
        """Test creating empty overview."""
        overview = TraefikOverview()
        
        assert overview.total_routers == 0
        assert overview.total_services == 0
        assert overview.total_middlewares == 0
        assert overview.total_entrypoints == 0


class TestTraefikVersion:
    """Test cases for TraefikVersion model."""
    
    def test_version_creation(self):
        """Test creating version info."""
        version = TraefikVersion(
            version="v3.0.0",
            codename="chevrotin",
            build_date="2024-01-01"
        )
        
        assert version.version == "v3.0.0"
        assert version.codename == "chevrotin"
        assert version.build_date == "2024-01-01"


class TestHealthStatus:
    """Test cases for HealthStatus model."""
    
    def test_health_status_creation(self):
        """Test creating health status."""
        health = HealthStatus(
            healthy=True,
            message="All systems operational",
            version="v3.0.0",
            uptime="24h30m"
        )
        
        assert health.healthy is True
        assert health.message == "All systems operational"
        assert health.version == "v3.0.0"
        assert health.uptime == "24h30m"
