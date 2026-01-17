"""
Integration tests for the MCP server
"""
import asyncio
import os
import pytest
from unittest.mock import AsyncMock, patch

from traefik_mcp.server import list_tools, call_tool, initialize_client


class TestServerIntegration:
    """Integration tests for the MCP server."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that tools are listed correctly."""
        tools = await list_tools()
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "get_traefik_overview",
            "list_routers",
            "get_router_details",
            "list_services",
            "get_service_details",
            "list_middlewares"
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
        
        result = await call_tool("get_traefik_overview", {})
        
        assert len(result) == 1
        assert "Traefik client not initialized" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_unknown_tool(self):
        """Test calling an unknown tool."""
        import traefik_mcp.server
        traefik_mcp.server.query_tools = AsyncMock()
        
        result = await call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert "Unknown tool: unknown_tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_with_error(self):
        """Test tool call with error handling."""
        import traefik_mcp.server
        traefik_mcp.server.query_tools = AsyncMock()
        traefik_mcp.server.query_tools.get_overview.side_effect = Exception("Test error")
        
        result = await call_tool("get_traefik_overview", {})
        
        assert len(result) == 1
        assert "Error executing get_traefik_overview: Test error" in result[0].text
