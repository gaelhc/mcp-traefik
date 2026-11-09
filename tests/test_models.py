"""
Tests for Traefik Data Models
"""
import pytest
from pydantic import ValidationError

from traefik_mcp.traefik.models import (
    Router, Service, Middleware, EntryPoint, 
    Overview, Version, HealthStatus
)


class TestRouter:
    """Test cases for Router model."""
    
    def test_router_creation(self):
        """Test creating a router with valid data."""
        router = Router(
            name="test-router",
            protocol="http",
            provider="docker",
            rule="Host(`example.com`)",
            status="enabled",
            service="test-service",
            entryPoints=["web", "secure"],
            middlewares=["headers","check-ip"],
            observability={'metrics': True},
            priority=10,
            using=["test-service"]
        )
       
        assert router.name == "test-router"
        assert router.protocol == "http"
        assert router.provider == "docker"
        assert router.rule == "Host(`example.com`)"
        assert router.status == "enabled"
        assert router.service == "test-service"
        assert router.entryPoints == ["web", "secure"]
        assert router.middlewares == ["headers","check-ip"]
        assert router.observability == {'metrics': True}
        assert router.priority == 10
        assert router.using == ["test-service"]

    def test_router_parsing(self):
        api_data = {
            "entryPoints":["traefik"],
            "service":"api@internal",
            "rule":"PathPrefix(`/api`)",
            "ruleSyntax":"v3",
            "priority":9223372036854775806,
            "observability":{
                "accessLogs":True,
                "tracing":True,
                "metrics":True
                },
            "status":"enabled",
            "using":["traefik"],
            "name":"api@internal",
            "provider":"internal"
            }
        
        api_data = Router.parseData(protocol='http', data=api_data)
        router = Router(**api_data)

        assert router.name == "api@internal"
        assert router.protocol == "http"
        assert router.provider == "internal"
        assert router.rule == "PathPrefix(`/api`)"
        assert router.status == "enabled"
        assert router.service == "api@internal"
        assert router.entryPoints == ["traefik"]
        assert router.middlewares == None
        assert router.observability == {"accessLogs":True, "tracing":True, "metrics":True}
        assert router.priority == 9223372036854775806
        assert router.using == ["traefik"]


class TestService:
    """Test cases for Service model."""
    
    def test_service_creation(self):
        """Test creating a router with valid data."""
        service = Service(
            name="test-service",
            protocol="http",
            provider="docker",
            status="enabled",
        )
       
        assert service.name == "test-service"
        assert service.protocol == "http"
        assert service.provider == "docker"
        assert service.status == "enabled"
        assert service.type == None
        assert service.serverStatus == []
        assert service.details == {}

    def test_service_parsing(self):
        api_data = {
            "loadBalancer":{
                "servers":[{"url":"http://public-cloud:80"}],
                "passHostHeader":True,
                "responseForwarding":{"flushInterval":"100ms"}
                },
            "status":"enabled",
            "usedBy":["cloud-router@file"],
            "serverStatus":{"http://public-cloud:80":"UP"},
            "name":"cloud-service@file",
            "provider":"file",
            "type":"loadbalancer"
            }

        api_data = Service.parseData(protocol='http', data=api_data)
        service = Service(**api_data)

        assert service.name == "cloud-service@file"
        assert service.protocol == "http"
        assert service.provider == "file"
        assert service.status == "enabled"
        assert service.type == "loadbalancer"
        assert service.serverStatus == {"http://public-cloud:80":"UP"}
        assert service.details == {
                "servers":[{"url":"http://public-cloud:80"}],
                "passHostHeader":True,
                "responseForwarding":{"flushInterval":"100ms"}
                }


class TestMiddleware:
    """Test cases for Middleware model."""

    def test_middleware_creation(self):
        """Test creating a router with valid data."""
        middleware = Middleware(
            name="test-service",
            protocol="http",
            provider="docker",
            type="chain",
            status="enabled",
            details={"middlewares":["headers","rate-limiter"]}
        )
       
        assert middleware.name == "test-service"
        assert middleware.protocol == "http"
        assert middleware.provider == "docker"
        assert middleware.status == "enabled"
        assert middleware.type == "chain"
        assert middleware.details == {"middlewares":["headers","rate-limiter"]}

    def test_middleware_parsing(self):
        api_data = {
            "chain":{
                "middlewares":[
                    "crowdsec-bouncer@file",
                    "geoip@file",
                    "geoblock-fr@file"
                    ]
                },
            "status":"enabled",
            "usedBy":[
                "authelia@file",
                "cloud-router@file"
                ],
            "name":"check-ip@file",
            "provider":"file",
            "type":"chain"
            }

        api_data = Middleware.parseData(protocol='http', data=api_data)
        middleware = Middleware(**api_data)

        assert middleware.name == "check-ip@file"
        assert middleware.protocol == "http"
        assert middleware.provider == "file"
        assert middleware.status == "enabled"
        assert middleware.type == "chain"
        assert middleware.details == {
                "middlewares":[
                    "crowdsec-bouncer@file",
                    "geoip@file",
                    "geoblock-fr@file"
                    ]
                }


    def test_middleware_parsing_2(self):
        api_data = {
            "plugin":{
                "geoblock":{
                    "allowLocalRequests":"true",
                    "allowUnknownCountries":"false",
                    "api":"https://get.geojs.io/v1/ip/country/{ip}",
                    "apiTimeoutMs":"750",
                    "cacheSize":"15",
                    "countries":["FR","CA"],
                    "forceMonthlyUpdate":"true",
                    "logAllowedRequests":"false",
                    "logApiRequests":"true",
                    "logLocalRequests":"false",
                    "unknownCountryApiResponse":"nil"
                    }
                },
            "status":"enabled",
            "name":"geoblock-fr@file",
            "provider":"file",
            "type":"geoblock"}

        api_data = Middleware.parseData(protocol='http', data=api_data)
        middleware = Middleware(**api_data)

        assert middleware.name == "geoblock-fr@file"
        assert middleware.protocol == "http"
        assert middleware.provider == "file"
        assert middleware.status == "enabled"
        assert middleware.type == "geoblock"
        assert middleware.details == {
                "geoblock":{
                    "allowLocalRequests":"true",
                    "allowUnknownCountries":"false",
                    "api":"https://get.geojs.io/v1/ip/country/{ip}",
                    "apiTimeoutMs":"750",
                    "cacheSize":"15",
                    "countries":["FR","CA"],
                    "forceMonthlyUpdate":"true",
                    "logAllowedRequests":"false",
                    "logApiRequests":"true",
                    "logLocalRequests":"false",
                    "unknownCountryApiResponse":"nil"
                    }
                }

class TestEntrypoint:
    """Test cases for Entrypoint model."""

    def test_entrypoint_creation(self):
        """Test creating a router with valid data."""
        entrypoint = EntryPoint(
            name="websecure",
            address=":443"
        )
       
        assert entrypoint.name == "websecure"
        assert entrypoint.address == ":443"
        assert entrypoint.http == None
        assert entrypoint.transport == None
        assert entrypoint.forwardedHeaders == None

    def test_entrypoint_parsing(self):
        api_data = {
            "address":":443",
            "transport":{
                "lifeCycle":{
                    "graceTimeOut":"10s"
                },
                "respondingTimeouts":{
                    "readTimeout":"30m0s",
                    "writeTimeout":"30m0s",
                    "idleTimeout":"3m0s"
                    }
                },
            "forwardedHeaders":{
                "trustedIPs":[
                    "127.0.0.1/32",
                    "192.168.1.0/24",
                    "100.64.0.0/10"
                    ]
                },
            "http":{
                "tls":{"options":"default"},
                "sanitizePath":True,
                "maxHeaderBytes":1048576
                },
            "http2":{"maxConcurrentStreams":250},
            "udp":{"timeout":"3s"},
            "name":"websecure"
            }

        api_data = EntryPoint.parseData(data=api_data)
        entrypoint = EntryPoint(**api_data)

        assert entrypoint.name == "websecure"
        assert entrypoint.address == ":443"
        assert entrypoint.http == {
                "tls":{"options":"default"},
                "sanitizePath":True,
                "maxHeaderBytes":1048576
                }
        assert entrypoint.transport == {
                "lifeCycle":{
                    "graceTimeOut":"10s"
                },
                "respondingTimeouts":{
                    "readTimeout":"30m0s",
                    "writeTimeout":"30m0s",
                    "idleTimeout":"3m0s"
                    }
                }
        assert entrypoint.forwardedHeaders == {
                "trustedIPs":[
                    "127.0.0.1/32",
                    "192.168.1.0/24",
                    "100.64.0.0/10"
                    ]
                }

class TestOverview:
    """Test cases for Overview model."""
    
    def test_overview_creation(self):
        """Test creating overview with data."""
        overview = Overview(
            http={"routers": {"total": 7}, "services": {"total": 3}, "middlewares": {"total": 1}},
            tcp={"routers": {"total": 0}, "services": {"total": 0}, "middlewares": {"total": 0}},
            udp={"routers": {"total": 0}, "services": {"total": 0}, "middlewares": {"total": 0}}
        )
        
        assert overview.total_routers == 7
        assert overview.total_services == 3
        assert overview.total_middlewares == 1
    
    def test_overview_empty(self):
        """Test creating empty overview."""
        overview = Overview()
        
        assert overview.total_routers == 0
        assert overview.total_services == 0
        assert overview.total_middlewares == 0


class TestVersion:
    """Test cases for Version model."""
    
    def test_version_creation(self):
        """Test creating version info."""
        version = Version(
            Version="v3.3.7",
            Codename="saintnectaire",
            startDate="2026-11-05T11:00:28.89169857+01:00"
        )
        
        assert version.version == "v3.3.7"
        assert version.codename == "saintnectaire"
        assert version.startdate == "2026-11-05T11:00:28.89169857+01:00"


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
