"""Tests for the Traefik MCP server."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys, os

sys.path.insert(0, '/home/gael/Depots/Ship/MCP-Traefik/src')

from traefik_mcp.server import overview, version, list_entrypoints, \
    entrypoint_details, list_routers, router_details, list_services, \
    service_details, list_middlewares, middleware_details
from traefik_mcp.traefik.api_client import TraefikClient


@pytest.fixture
async def mocked_traefik_client():
    """Create a mocked Traefik client."""
    client = MagicMock(spec=TraefikClient)
    client.get_overview = AsyncMock(return_value={
        "version": "2.9.0",
        "traefikVersion": "2.9.0",
        "serverTime": "2024-01-01T00:00:00Z"
    })
    client.get_version = AsyncMock(return_value={
        "Version": "2.9.0",
        "Codename": "MyTest",
        "startDate": "2026-11-05T11:00:28.89169857+01:00"
    })
    client.get_api_content = AsyncMock(side_effect=lambda endpoint:
        [] if "/entrypoints" in endpoint else MagicMock())
    return client


@pytest.fixture
def environ():
    """Set up environment variables for Traefik."""
    with patch.dict(os.environ, {
        "TRAEFIK_API_URL": "http://localhost:8080",
        "TRAEFIK_API_KEY": "test_api_key",
        "MCP_TIMEOUT": "30.0"
    }):
        yield


# ============= Overview tests =============

async def test_overview_structured(mocked_traefik_client):
    """Test overview tool with structured output."""
    with patch('traefik_mcp.server.get_client') as mock_get:
        mock_get.return_value = mocked_traefik_client
        result = await overview(output_format='structured')
        t = result['overview']
        
        assert 'request' in result
        assert 'overview' in result
        assert result['overview'].http == {}
        assert result['overview'].tcp == {}
        assert result['overview'].udp == {}
        assert result['overview'].features == {}
        assert result['overview'].total_routers == 0
        assert result['overview'].total_services == 0
        assert result['overview'].total_middlewares == 0


async def test_overview_markdown(mocked_traefik_client):
    """Test overview tool with markdown output."""
    with patch('traefik_mcp.server.get_client') as mock_get:
        mock_get.return_value = mocked_traefik_client
        result = await overview(output_format='markdown')
        assert 'request' in result
        assert 'overview' in result
        assert isinstance(result['overview'], str)


# ============= Version tests =============

async def test_version_structured(mocked_traefik_client):
    """Test version tool with structured output."""
    with patch('traefik_mcp.server.get_client') as mock_get:
        mock_get.return_value = mocked_traefik_client
        result = await version(output_format='structured')
        assert 'request' in result
        assert 'version' in result
        assert result['version'].version == '2.9.0'


async def test_version_markdown(mocked_traefik_client):
    """Test version tool with markdown output."""
    with patch('traefik_mcp.server.get_client') as mock_get:
        mock_get.return_value = mocked_traefik_client
        result = await version(output_format='markdown')
        assert 'request' in result
        assert 'version' in result
        assert isinstance(result['version'], str)
