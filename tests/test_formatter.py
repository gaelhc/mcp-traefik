"""
Tests pour les outils de requête Traefik.

Ce module contient les tests unitaires pour les fonctions de formatage
dans query_tools.py.
"""
import pytest
from traefik_mcp.tools.query_tools import Formatter
from traefik_mcp.traefik.models import Models


@pytest.fixture
def mock_traefik_overview():
    """Fixture avec des données d'overview typiques."""
    data = {
        "http": {
            "routers": {"total": 3},
            "services": {"total": 8},
            "middlewares": {"total": 5}
        },
        "tcp": {
            "routers": {"total": 2},
            "services": {"total": 4},
            "middlewares": {"total": 3}
        },
        "udp": {
            "routers": {"total": 0},
            "services": {"total": 0},
            "middlewares": {"total": 0}
        },
        "features": {
            "traefik-v1": "true",
            "global": "enabled"
        },
        "providers": [
            "default",
            "local"
        ]
    }
    return Models.Overview(**data)

@pytest.fixture
def mock_version():
    """Fixture avec des données de version typiques."""
    data = {
        "Version": "1.2.3",
        "Codename": "test-codename",
        "startDate": "1592-14-03"
    }
    return Models.Version(**data)

@pytest.fixture
def mock_middleware_base():
    """Fixture avec des données de version typiques."""
    data = {
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
    data = Models.Middleware.parseData(protocol='http',data=data)
    return Models.Middleware(**data)


@pytest.fixture
def mock_middleware_1():
    """Fixture avec des données de version typiques."""
    data = {
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
    data = Models.Middleware.parseData(protocol='http',data=data)
    return Models.MiddlewareDetails(**data)
    
@pytest.fixture
def mock_middleware_2():
    """Fixture avec des données de version typiques."""
    data = {
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
        "type":"geoblock"
        }
    data = Models.Middleware.parseData(protocol='http',data=data)
    return Models.MiddlewareDetails(**data)

@pytest.fixture
def mock_router_base():
    data = {
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
    data = Models.Router.parseData(protocol='http',data=data)
    return Models.Router(**data)

@pytest.fixture
def mock_router():
    data = {
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
    data = Models.Router.parseData(protocol='http',data=data)
    return Models.RouterDetails(**data)

@pytest.fixture
def mock_service_base():
    data = {
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
    data = Models.Service.parseData(protocol='http',data=data)
    return Models.Service(**data)

@pytest.fixture
def mock_service():
    data = {
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
    data = Models.Service.parseData(protocol='http',data=data)
    return Models.ServiceDetails(**data)

@pytest.fixture
def mock_entrypoint_base():
    data = {
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
    data = Models.EntryPoint.parseData(data=data)
    return Models.EntryPoint(**data)

@pytest.fixture
def mock_entrypoint():
    data = {
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
    data = Models.EntryPoint.parseData(data=data)
    return Models.EntryPointDetails(**data)




class TestFormatOverview:
    
    def test_format_overview_basic(self, mock_traefik_overview):
        result = Formatter.format_overview(mock_traefik_overview)
        
        assert "# Traefik Overview" in result
        assert "http" in result
        assert "tcp" in result
        assert "udp" in result
        assert "entrypoint" in result
        
        assert "5" in result
        assert "12" in result
        assert "8" in result
    
    def test_format_overview_section_titles(self, mock_traefik_overview):
        result = Formatter.format_overview(mock_traefik_overview)
        
        assert "**Routers**" in result
        assert "**Middlewares**" in result
        assert "**Services**" in result
        assert "**Entrypoints**" in result
        assert "**Protocols**" in result
        assert "## Summary" in result
        
class TestFormatVersion:

    def test_format_version_basic(self, mock_version):
        result = Formatter.format_version(mock_version)
        
        assert "# Traefik version" in result
        assert "**Version**" in result
        assert "**Codename**" in result
        assert "**Start Date**" in result

        assert "1.2.3" in result
        assert "test-codename" in result
        assert "1592-14-03" in result

class TestFormatMiddleware:

    def test_format_middleware_short(self, mock_middleware_base):
        result = Formatter.format_middleware(mock_middleware_base)
        
        assert "## Middleware" in result
        assert "**protocol**" in result
        assert "**provider**" in result
        assert "**type**" in result
        assert "**status**" in result

        assert "check-ip@file" in result
        assert "chain" in result
        assert "enabled" in result

    def test_format_middleware_long(self, mock_middleware_2):
        result = Formatter.format_middleware(mock_middleware_2)

        assert "FR" in result
        assert "geoblock" in result
        assert "unknownCountryApiResponse" in result

class TestFormatRouter:

    def test_format_router_short(self, mock_router_base):
        result = Formatter.format_router(mock_router_base)
        
        assert "## Router" in result
        assert "**protocol**" in result
        assert "**provider**" in result
        assert "**status**" in result

        assert "api@internal" in result
        assert "enabled" in result

    def test_format_router_long(self, mock_router):
        result = Formatter.format_router(mock_router)

        assert "**service**" in result
        assert "**rule**" in result

        assert "PathPrefix(`/api`)" in result
        assert "traefik" in result
        assert "priority" in result
        assert "observability" in result
        assert "metrics" in result

class TestFormatService:

    def test_format_service_short(self, mock_service_base):
        result = Formatter.format_service(mock_service_base)
        
        assert "## Service" in result
        assert "**protocol**" in result
        assert "**provider**" in result
        assert "**type**" in result

        assert "cloud-service@file" in result

    def test_format_service_long(self, mock_service):
        result = Formatter.format_service(mock_service)

        assert "**server status**" in result
        assert "http://public-cloud:80" in result
        assert "passHostHeader" in result
        assert "flushInterval" in result
        assert "url" in result

class TestFormatEntryPoint:

    def test_format_entrypoint_short(self, mock_entrypoint_base):
        result = Formatter.format_entrypoint(mock_entrypoint_base)
        
        assert "## Entrypoint" in result
        assert "**address**" in result

        assert ":443" in result

    def test_format_entrypoint_long(self, mock_entrypoint):
        result = Formatter.format_entrypoint(mock_entrypoint)

        assert "**http**" in result
        assert "**transport**" in result
        assert "**forwarded headers**" in result
        assert "**life cyle**" in result
        
        assert "tls" in result
        assert "timeout" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
