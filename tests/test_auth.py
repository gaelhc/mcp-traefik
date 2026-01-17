"""
Tests for basic authentication functionality in TraefikClient.
"""
import asyncio
import base64
from unittest.mock import AsyncMock, patch

import pytest

from traefik_mcp.traefik.api_client import TraefikClient


class TestBasicAuthentication:
    """Test suite for basic authentication functionality."""

    def test_basic_auth_headers(self):
        """Test that basic auth headers are correctly formatted."""
        client = TraefikClient(
            api_url="http://localhost:8080",
            basic_auth_username="testuser",
            basic_auth_password="testpass"
        )
        
        expected_credentials = base64.b64encode("testuser:testpass".encode()).decode()
        expected_header = f"Basic {expected_credentials}"
        
        assert client.headers.get('Authorization') == expected_header

    def test_api_key_priority(self):
        """Test that API key takes precedence over basic auth."""
        client = TraefikClient(
            api_url="http://localhost:8080",
            api_key="test-api-key",
            basic_auth_username="testuser",
            basic_auth_password="testpass"
        )
        
        expected_header = "Bearer test-api-key"
        assert client.headers.get('Authorization') == expected_header

    def test_no_auth(self):
        """Test that no Authorization header is set when no credentials provided."""
        client = TraefikClient(api_url="http://localhost:8080")
        
        assert 'Authorization' not in client.headers

    @pytest.mark.asyncio
    async def test_basic_auth_request(self):
        """Test that basic auth is used in actual requests."""
        client = TraefikClient(
            api_url="http://localhost:8080",
            basic_auth_username="testuser",
            basic_auth_password="testpass"
        )
        
        # Mock the httpx client
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_client.request.return_value = mock_response
            
            # Make a request
            result = await client._make_request('GET', '/api/overview')
            
            # Verify the request was made with correct headers
            mock_client.request.assert_called_once()
            
            # Check that Authorization header is present in the client headers
            client_headers = mock_client_class.call_args[1]['headers']
            assert 'Authorization' in client_headers
            assert client_headers['Authorization'].startswith('Basic ')

    def test_basic_auth_credentials_encoding(self):
        """Test that special characters in credentials are properly encoded."""
        client = TraefikClient(
            api_url="http://localhost:8080",
            basic_auth_username="user@email.com",
            basic_auth_password="p@ssw0rd!"
        )
        
        expected_credentials = base64.b64encode("user@email.com:p@ssw0rd!".encode()).decode()
        expected_header = f"Basic {expected_credentials}"
        
        assert client.headers.get('Authorization') == expected_header

    def test_partial_basic_auth_credentials(self):
        """Test that partial basic auth credentials don't set header."""
        # Only username provided
        client1 = TraefikClient(
            api_url="http://localhost:8080",
            basic_auth_username="testuser"
        )
        assert 'Authorization' not in client1.headers
        
        # Only password provided
        client2 = TraefikClient(
            api_url="http://localhost:8080",
            basic_auth_password="testpass"
        )
        assert 'Authorization' not in client2.headers
