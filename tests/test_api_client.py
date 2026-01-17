"""
Tests for Traefik API Client
"""
import pytest
from unittest.mock import AsyncMock, patch

from traefik_mcp.traefik.api_client import TraefikClient, TraefikError, TraefikConnectionError


class TestTraefikClient:
    """Test cases for TraefikClient."""
    
    def test_client_initialization(self):
        """Test client initialization with and without API key."""
        # Test without API key
        client = TraefikClient("http://localhost:8080")
        assert client.api_url == "http://localhost:8080"
        assert client.api_key is None
        assert "Authorization" not in client.headers
        
        # Test with API key
        client = TraefikClient("http://localhost:8080", api_key="test-key")
        assert client.api_key == "test-key"
        assert client.headers["Authorization"] == "Bearer test-key"
    
    def test_client_initialization_strips_trailing_slash(self):
        """Test that trailing slash is stripped from API URL."""
        client = TraefikClient("http://localhost:8080/")
        assert client.api_url == "http://localhost:8080"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with patch.object(TraefikClient, 'get_overview', new_callable=AsyncMock) as mock_overview:
            mock_overview.return_value = {"router": {"docker": 5}}
            
            client = TraefikClient("http://localhost:8080")
            result = await client.health_check()
            
            assert result is True
            mock_overview.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check when API call fails."""
        with patch.object(TraefikClient, 'get_overview', new_callable=AsyncMock) as mock_overview:
            mock_overview.side_effect = TraefikError("Connection failed")
            
            client = TraefikClient("http://localhost:8080")
            result = await client.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_overview(self):
        """Test getting overview data."""
        mock_response = {
            "router": {"docker": 5, "file": 2},
            "service": {"docker": 3},
            "middleware": {"file": 1}
        }
        
        with patch.object(TraefikClient, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            client = TraefikClient("http://localhost:8080")
            result = await client.get_overview()
            
            assert result == mock_response
            mock_request.assert_called_once_with('GET', '/api/overview')
    
    @pytest.mark.asyncio
    async def test_get_routers(self):
        """Test getting routers data."""
        mock_response = {
            "router1@docker": {
                "rule": "Host(`example.com`)",
                "service": "service1@docker",
                "status": "enabled"
            },
            "router2@docker": {
                "rule": "Host(`test.com`)",
                "service": "service2@docker",
                "status": "enabled"
            }
        }
        
        with patch.object(TraefikClient, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            client = TraefikClient("http://localhost:8080")
            result = await client.get_routers()
            
            assert len(result) == 2
            assert result[0]["rule"] == "Host(`example.com`)"
            assert result[1]["rule"] == "Host(`test.com`)"
            mock_request.assert_called_once_with('GET', '/api/http/routers')
    
    @pytest.mark.asyncio
    async def test_get_routers_with_provider(self):
        """Test getting routers with provider filter."""
        with patch.object(TraefikClient, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}
            
            client = TraefikClient("http://localhost:8080")
            await client.get_routers(provider="docker")
            
            mock_request.assert_called_once_with('GET', '/api/http/routers?provider=docker')
    
    @pytest.mark.asyncio
    async def test_get_services(self):
        """Test getting services data."""
        mock_response = {
            "service1@docker": {
                "loadBalancer": {
                    "servers": [
                        {"url": "http://localhost:8081", "weight": 1}
                    ]
                }
            }
        }
        
        with patch.object(TraefikClient, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            client = TraefikClient("http://localhost:8080")
            result = await client.get_services()
            
            assert len(result) == 1
            assert "loadBalancer" in result[0]
            mock_request.assert_called_once_with('GET', '/api/http/services')
    
    @pytest.mark.asyncio
    async def test_get_middlewares(self):
        """Test getting middlewares data."""
        mock_response = {
            "middleware1@docker": {
                "addPrefix": {
                    "prefix": "/api"
                }
            }
        }
        
        with patch.object(TraefikClient, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            client = TraefikClient("http://localhost:8080")
            result = await client.get_middlewares()
            
            assert len(result) == 1
            assert "addPrefix" in result[0]
            mock_request.assert_called_once_with('GET', '/api/http/middlewares')
    
    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test handling of authentication errors."""
        import httpx
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            client = TraefikClient("http://localhost:8080", api_key="wrong-key")
            
            with pytest.raises(TraefikError) as exc_info:
                await client._make_request('GET', '/api/overview')
            
            assert "Authentication failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_not_found_error(self):
        """Test handling of 404 errors."""
        import httpx
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_client.return_value.__aenter__.return_value.request.return_value = mock_response
            
            client = TraefikClient("http://localhost:8080")
            
            with pytest.raises(TraefikError) as exc_info:
                await client._make_request('GET', '/api/nonexistent')
            
            assert "Endpoint not found" in str(exc_info.value)
