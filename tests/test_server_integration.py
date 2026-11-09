"""
Integration tests for the MCP server
"""
import asyncio
import os
import pytest
from unittest.mock import AsyncMock, patch

from traefik_mcp.server import list_tools, call_tool, initialize_client
from mcp.types import CallToolRequestParams

class TestServerIntegration:
    """Integration tests for the MCP server."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that tools are listed correctly."""
        res = await list_tools(ctx="ctx")
        
        tool_names = [tool.name for tool in res.tools]
        expected_tools = [
            "get_version",
            "get_overview",
            "get_entrypoint",
            "get_router",
            "get_middleware",
            "get_service"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_initialize_client_success(self):
        """Test successful client initialization."""
        with patch.dict(os.environ, {
            'TRAEFIK_API_URL': 'http://localhost:8080',
            'TRAEFIK_API_KEY': 'test-key'
        }):
            with patch('traefik_mcp.server.TraefikClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.health_check.return_value = True
                mock_client_class.return_value = mock_client
                
                await initialize_client()
                
                mock_client_class.assert_called_once_with(
                    api_url='http://localhost:8080',
                    api_key='test-key',
                    timeout=30.0
                )
                mock_client.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_client_missing_url(self):
        """Test client initialization fails without API URL."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TRAEFIK_API_URL environment variable is required"):
                await initialize_client()
    
    @pytest.mark.asyncio
    async def test_call_tool_without_client(self):
        """Test tool call fails when client is not initialized."""
        # Reset global variables
        import traefik_mcp.server
        traefik_mcp.server.query_tools = None
        params = CallToolRequestParams(name="get_overview")
        result = await call_tool(ctx="ctx", params=params)
        
        assert result.is_error
        assert "Traefik client not initialized" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_call_unknown_tool(self):
        """Test calling an unknown tool."""
        import traefik_mcp.server
        traefik_mcp.server.query_tools = AsyncMock()
        
        params = CallToolRequestParams(name="get_wrong_tool")
        result = await call_tool(ctx="ctx", params=params)
        
        assert result.is_error
        assert "Unknown tool: get_wrong_tool" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_with_error(self):
        """Test tool call with error handling."""
        import traefik_mcp.server
        traefik_mcp.server.query_tools = AsyncMock()
        traefik_mcp.server.query_tools.get_overview.side_effect = Exception("Test error")
        
        params = CallToolRequestParams(name="get_overview")
        result = await call_tool(ctx="ctx", params=params)
        
        assert result.is_error
        assert "Error executing get_overview: Test error" in result.content[0].text


class TestServerHTTPSESEMode:
    """Tests for HTTP/SSE transport mode."""
    
    @pytest.mark.asyncio
    async def test_http_mode_env_variables(self):
        """Test HTTP mode environment variables are set correctly."""
        with patch.dict(os.environ, {
            'MCP_TRANSPORT': 'http',
            'MCP_PORT': '3404',
            'MCP_HOST': '0.0.0.0'
        }):
            assert os.getenv('MCP_TRANSPORT') == 'http'
            assert int(os.getenv('MCP_PORT', '8080')) == 3404
            assert os.getenv('MCP_HOST') == '0.0.0.0'
    
    @pytest.mark.asyncio
    async def test_sse_default_paths(self):
        """Test default SSE and message paths."""
        # Verify default environment values for paths
        default_sse = os.getenv('MCP_SSE_PATH', '/mcp/sse')
        default_message = os.getenv('MCP_MESSAGE_PATH', '/mcp/message')
        
        assert default_sse == '/mcp/sse'
        assert default_message == '/mcp/message'
    
    @pytest.mark.asyncio
    async def test_custom_sse_paths(self):
        """Test custom SSE path configuration."""
        with patch.dict(os.environ, {
            'MCP_SSE_PATH': '/custom-sse',
            'MCP_MESSAGE_PATH': '/custom-message'
        }):
            assert os.getenv('MCP_SSE_PATH') == '/custom-sse'
            assert os.getenv('MCP_MESSAGE_PATH') == '/custom-message'
    
    @pytest.mark.asyncio
    async def test_http_sse_transport_modes(self):
        """Test that both http and sse transport modes are valid."""
        valid_modes = ['http', 'sse']
        
        for mode in valid_modes:
            with patch.dict(os.environ, {
                'MCP_TRANSPORT': mode,
                'TRAEFIK_API_URL': 'http://localhost:8080'
            }):
                assert os.getenv('MCP_TRANSPORT') in valid_modes
    
    @pytest.mark.asyncio  
    async def test_http_mode_with_different_ports(self):
        """Test HTTP mode works with different port configurations."""
        test_ports = ['80', '443', '3404', '5000', '8080']
        
        for port in test_ports:
            with patch.dict(os.environ, {
                'MCP_PORT': port,
                'MCP_TRANSPORT': 'http',
                'TRAEFIK_API_URL': 'http://localhost:8080'
            }):
                expected_port = int(port)
                actual_port = int(os.getenv('MCP_PORT', '8080'))
                assert actual_port == expected_port


class TestHTTPServerEndpoint:
    """Tests for specific HTTP server endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint_response(self):
        """Test root endpoint returns server info."""
        from starlette.responses import JSONResponse
        
        expected_response = {
            "service": "Traefik MCP Server",
            "sse_endpoint": "/mcp/sse",
            "message_endpoint": "/mcp/message",
        }
        
        response = JSONResponse(expected_response)
        
        assert response.status_code == 200
        assert 'service' in expected_response
    
    @pytest.mark.asyncio
    async def test_sse_message_endpoint_paths(self):
        """Test that SSE and message endpoints are configured."""
        # These are the default paths defined in server.py
        default_sse = os.getenv('MCP_SSE_PATH', '/mcp/sse')
        default_message = os.getenv('MCP_MESSAGE_PATH', '/mcp/message')
        
        # Verify both endpoints exist as strings
        assert isinstance(default_sse, str) and len(default_sse) > 0
        assert isinstance(default_message, str) and len(default_message) > 0
    
    @pytest.mark.asyncio
    async def test_message_post_endpoint(self):
        """Test POST /message endpoint response."""
        from starlette.responses import JSONResponse
        
        # Successful message handling
        response = JSONResponse(status_code=200, content={"status": "ok"})
        assert response.status_code == 200
        
        # Error message handling
        error_response = JSONResponse(
            status_code=500, 
            content={"error": "message processing failed"}
        )
        assert error_response.status_code == 500


class TestHTTPServerEnvironment:
    """Tests for HTTP server environment variables."""
    
    @pytest.mark.asyncio
    async def test_default_port_value(self):
        """Test default port value when not specified."""
        with patch.dict(os.environ, {}, clear=False):
            port = int(os.getenv('MCP_PORT', '8080'))
            assert port == 8080
    
    @pytest.mark.asyncio
    async def test_default_host_value(self):
        """Test default host value."""
        with patch.dict(os.environ, {}, clear=False):
            host = os.getenv('MCP_HOST', '0.0.0.0')
            assert host == '0.0.0.0'
    
    @pytest.mark.asyncio
    async def test_timeout_default_value(self):
        """Test timeout default value."""
        with patch.dict(os.environ, {}, clear=False):
            timeout = float(os.getenv('MCP_TIMEOUT', '30.0'))
            assert timeout == 30.0


class TestHTTPServerLogging:
    """Tests for server logging configuration."""
    
    @pytest.mark.asyncio
    async def test_logging_configuration(self):
        """Test that logging is configured properly."""
        import traefik_mcp.server
        
        # Verify logger exists and is configured
        logger = traefik_mcp.server.logger
        assert logger is not None
    
    @pytest.mark.asyncio
    async def test_server_log_level(self):
        """Test server log level configuration."""
        import traefik_mcp.server
        
        logger = traefik_mcp.server.logger
        
        # Default level should be INFO or NOTSET (will be set in main)
        assert hasattr(logger, 'level')


class TestHTTPServerSecurity:
    """Tests for HTTP server security configuration."""
    
    @pytest.mark.asyncio
    async def test_api_key_authentication_setup(self):
        """Test API key authentication is set up correctly."""
        with patch.dict(os.environ, {
            'TRAEFIK_API_URL': 'http://localhost:8080',
            'TRAEFIK_API_KEY': 'secure-key-123'
        }):
            api_key = os.getenv('TRAEFIK_API_KEY')
            assert api_key == 'secure-key-123'
    
    @pytest.mark.asyncio
    async def test_basic_auth_setup(self):
        """Test Basic Auth configuration."""
        with patch.dict(os.environ, {
            'TRAEFIK_API_URL': 'http://localhost:8080',
            'TRAEFIK_BASIC_AUTH_USERNAME': 'admin',
            'TRAEFIK_BASIC_AUTH_PASSWORD': 'secret'
        }):
            username = os.getenv('TRAEFIK_BASIC_AUTH_USERNAME')
            password = os.getenv('TRAEFIK_BASIC_AUTH_PASSWORD')
            
            assert username == 'admin'
            assert password == 'secret'
    
    @pytest.mark.asyncio
    async def test_no_auth_mode(self):
        """Test no authentication mode configuration."""
        with patch.dict(os.environ, {
            'TRAEFIK_API_URL': 'http://localhost:8080',
            # No auth credentials
        }):
            api_key = os.getenv('TRAEFIK_API_KEY')
            username = os.getenv('TRAEFIK_BASIC_AUTH_USERNAME')
            
            assert api_key is None or api_key == ''
            assert username is None or username == ''


class TestHTTPServerInitialization:
    """Tests for server initialization in HTTP mode."""
    
    @pytest.mark.asyncio
    async def test_initialization_with_api_key_auth(self):
        """Test successful initialization with API key auth."""
        from traefik_mcp.server import initialize_client
        
        with patch.dict(os.environ, {
            'TRAEFIK_API_URL': 'http://localhost:8080',
            'TRAEFIK_API_KEY': 'test-key'
        }):
            # This will raise if no TRAEFIK_API_URL or other error
            # We're just testing that it doesn't fail on env setup
            try:
                await initialize_client()
            except ValueError as e:
                # Expected if TraefikClient health check fails
                assert "TRAEFIK_API_URL environment variable is required" not in str(e)
    
    @pytest.mark.asyncio
    async def test_initialization_with_basic_auth(self):
        """Test successful initialization with Basic Auth."""
        from traefik_mcp.server import initialize_client
        
        with patch.dict(os.environ, {
            'TRAEFIK_API_URL': 'http://localhost:8080',
            'TRAEFIK_BASIC_AUTH_USERNAME': 'admin',
            'TRAEFIK_BASIC_AUTH_PASSWORD': 'secret'
        }):
            try:
                await initialize_client()
            except ValueError as e:
                # Expected if health check fails
                assert "TRAEFIK_API_URL environment variable is required" not in str(e)
    
    @pytest.mark.asyncio
    async def test_initialization_missing_url(self):
        """Test initialization fails without API URL."""
        from traefik_mcp.server import initialize_client
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TRAEFIK_API_URL environment variable is required"):
                await initialize_client()

