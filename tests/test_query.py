"""Tests for QueryTools."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.types import TextContent
from traefik_mcp.tools.query_tools import QueryTools


class TestQueryToolsGetOverview(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_overview method of QueryTools."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock client that returns sample data
        self.mock_client = MagicMock()
        
        self.sample_data = {
            "totalRouters": 12,
            "totalServices": 12,
            "totalMiddlewares": 16,
            "router": {
                "http": 12,
                "tcp": 0,
                "udp": 0,
            },
            "service": {
                "http": 12,
                "tcp": 0,
                "udp": 0,
            },
            "middleware": {
                "http": 16,
                "tcp": 0,
                "udp": 0,
            },
            "features": {
                "tracing": "",
                "metrics": "Prometheus",
                "accessLog": "True",
            },
            "providers": ["File"],
        }

    async def tearDown(self):
        """Clean up after tests."""
        pass

    @patch("traefik_mcp.tools.query_tools.TraefikClient")
    async def test_get_overview_successful(self, mock_client_class):
        """Test successful overview retrieval with sample data."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        # Mock the get_overview method to return our sample data
        mock_instance.get_overview = AsyncMock(return_value=self.sample_data)
        
        # Create QueryTools instance with mocked client
        query_tools = QueryTools(client=mock_instance)
        
        # Call the method
        result = await query_tools.get_overview()
        
        # Verify the result is a list containing TextContent
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].type, "text")



class TestQueryToolsGetVersion(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_version method of QueryTools."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock client that returns sample data
        self.mock_client = MagicMock()
        
        self.sample_data = {
            "Version": "1.2.3",
            "Codename": "test-codename",
            "startDate": "1592-14-03"
            }

    async def tearDown(self):
        """Clean up after tests."""
        pass

    @patch("traefik_mcp.tools.query_tools.TraefikClient")
    async def test_get_version(self, mock_client_class):
        """Test successful overview retrieval with sample data."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        # Mock the get_overview method to return our sample data
        mock_instance.get_version = AsyncMock(return_value=self.sample_data)
        
        # Create QueryTools instance with mocked client
        query_tools = QueryTools(client=mock_instance)
        
        # Call the method
        result = await query_tools.get_version()
        
        # Verify the result is a list containing TextContent
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].type, "text")


class TestQueryToolsGetEntrypoint(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_entrypoint method of QueryTools."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock client that returns sample data
        self.mock_client = MagicMock()
        
        self.sample_data = {
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

    async def tearDown(self):
        """Clean up after tests."""
        pass

    @patch("traefik_mcp.tools.query_tools.TraefikClient")
    async def test_get_version(self, mock_client_class):
        """Test successful overview retrieval with sample data."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        # Mock the get_overview method to return our sample data
        mock_instance.get_api_content = AsyncMock(return_value=self.sample_data)
        
        # Create QueryTools instance with mocked client
        query_tools = QueryTools(client=mock_instance)
        
        # Call the method
        result = await query_tools.get_entrypoint(name="websecure")
        
        # Verify the result is a list containing TextContent
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].type, "text")

class TestQueryToolsGetRouter(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_router method of QueryTools."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock client that returns sample data
        self.mock_client = MagicMock()
        
        self.sample_data = {
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

    async def tearDown(self):
        """Clean up after tests."""
        pass

    @patch("traefik_mcp.tools.query_tools.TraefikClient")
    async def test_get_router(self, mock_client_class):
        """Test successful overview retrieval with sample data."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        # Mock the get_overview method to return our sample data
        mock_instance.get_api_content = AsyncMock(return_value=self.sample_data)
        
        # Create QueryTools instance with mocked client
        query_tools = QueryTools(client=mock_instance)
        
        # Call the method
        result = await query_tools.get_router(protocol='http',name="api@internal")
        
        # Verify the result is a list containing TextContent
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].type, "text")

class TestQueryToolsGetMiddleware(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_router method of QueryTools."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock client that returns sample data
        self.mock_client = MagicMock()
        
        self.sample_data = {
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

    async def tearDown(self):
        """Clean up after tests."""
        pass

    @patch("traefik_mcp.tools.query_tools.TraefikClient")
    async def test_get_middleware(self, mock_client_class):
        """Test successful overview retrieval with sample data."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        # Mock the get_overview method to return our sample data
        mock_instance.get_api_content = AsyncMock(return_value=self.sample_data)
        
        # Create QueryTools instance with mocked client
        query_tools = QueryTools(client=mock_instance)
        
        # Call the method
        result = await query_tools.get_router(protocol='http',name="check-ip@file")
        
        # Verify the result is a list containing TextContent
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].type, "text")

class TestQueryToolsGetService(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_router method of QueryTools."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock client that returns sample data
        self.mock_client = MagicMock()
        
        self.sample_data = {
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

    async def tearDown(self):
        """Clean up after tests."""
        pass

    @patch("traefik_mcp.tools.query_tools.TraefikClient")
    async def test_get_service(self, mock_client_class):
        """Test successful overview retrieval with sample data."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        # Mock the get_overview method to return our sample data
        mock_instance.get_api_content = AsyncMock(return_value=self.sample_data)
        
        # Create QueryTools instance with mocked client
        query_tools = QueryTools(client=mock_instance)
        
        # Call the method
        result = await query_tools.get_service(protocol='http',name="cloud-service@file")
        
        # Verify the result is a list containing TextContent
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].type, "text")


if __name__ == "__main__":
    unittest.main()
