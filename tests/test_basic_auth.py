#!/usr/bin/env python3
"""
Test script to verify basic authentication implementation.
"""
import os
import sys
import asyncio
import base64
from unittest.mock import AsyncMock, patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from traefik_mcp.traefik.api_client import TraefikClient


def test_basic_auth_headers():
    """Test that basic auth headers are correctly formatted."""
    print("Testing basic auth header generation...")
    
    # Test with basic auth credentials
    client = TraefikClient(
        api_url="http://localhost:8080",
        basic_auth_username="testuser",
        basic_auth_password="testpass"
    )
    
    expected_credentials = base64.b64encode("testuser:testpass".encode()).decode()
    expected_header = f"Basic {expected_credentials}"
    
    assert client.headers.get('Authorization') == expected_header, \
        f"Expected {expected_header}, got {client.headers.get('Authorization')}"
    
    print("✓ Basic auth headers correctly formatted")


def test_api_key_priority():
    """Test that API key takes precedence over basic auth."""
    print("Testing API key precedence over basic auth...")
    
    client = TraefikClient(
        api_url="http://localhost:8080",
        api_key="test-api-key",
        basic_auth_username="testuser",
        basic_auth_password="testpass"
    )
    
    expected_header = "Bearer test-api-key"
    
    assert client.headers.get('Authorization') == expected_header, \
        f"Expected {expected_header}, got {client.headers.get('Authorization')}"
    
    print("✓ API key correctly takes precedence over basic auth")


def test_no_auth():
    """Test that no Authorization header is set when no credentials provided."""
    print("Testing no authentication...")
    
    client = TraefikClient(api_url="http://localhost:8080")
    
    assert 'Authorization' not in client.headers, \
        "No Authorization header should be set when no credentials provided"
    
    print("✓ No authentication headers correctly omitted")


async def test_basic_auth_request():
    """Test that basic auth is used in actual requests."""
    print("Testing basic auth in HTTP requests...")
    
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
        call_args = mock_client.request.call_args
        
        # Check that Authorization header is present and correctly formatted
        # The headers are passed to the AsyncClient constructor, not the request method
        client_headers = mock_client_class.call_args[1]['headers']
        assert 'Authorization' in client_headers, "Authorization header should be present"
        assert client_headers['Authorization'].startswith('Basic '), \
            "Authorization should use Basic scheme"
        
        print("✓ Basic auth correctly used in HTTP requests")


def main():
    """Run all tests."""
    print("Running basic authentication tests...\n")
    
    try:
        test_basic_auth_headers()
        test_api_key_priority()
        test_no_auth()
        
        # Run async test
        asyncio.run(test_basic_auth_request())
        
        print("\n✅ All tests passed! Basic authentication implementation is working correctly.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
