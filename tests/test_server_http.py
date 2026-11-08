import os
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
@patch("uvicorn.Server.serve", new_callable=AsyncMock)
@patch("traefik_mcp.server.initialize_client", new_callable=AsyncMock)
async def test_main_http_sse_transport(mock_init_client, mock_uvicorn_serve, monkeypatch):
    """Check main() for http/sse transport."""
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("TRAEFIK_API_URL", "http://localhost:8080")
    monkeypatch.setenv("MCP_SSE_PATH", "/custom/sse")
    monkeypatch.setenv("MCP_MESSAGE_PATH", "/custom/message")

    from traefik_mcp.server import main
    await main()

    mock_init_client.assert_awaited_once()
    mock_uvicorn_serve.assert_awaited_once()

@pytest.mark.asyncio
async def test_starlette_routes(monkeypatch):
    """Check starlette_app for http/sse transport."""
    monkeypatch.setenv("TRAEFIK_API_URL", "http://localhost:8080")
    from traefik_mcp.server import create_starlette_app 
    app = create_starlette_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "Traefik MCP Server"