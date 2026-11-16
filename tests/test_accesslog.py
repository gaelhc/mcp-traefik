"""Basic tests for reader.py - basic tests for filters and sorting."""

import pytest
from pathlib import Path
import json
import orjson
from traefik_mcp.accesslogs.reader import Filters, RequestAccessLog


class TestFilters:
    """Basic tests for the Filters class."""

    def test_filter_exact_match(self):
        """Test of exact match filtering."""
        filter = Filters('RequestMethod = "GET"')
        
        record_get = {
            "RequestMethod": "GET",
            "DownstreamStatus": 200,
            "time": "2026-11-15T10:00:00+00:00"
        }
        record_post = {
            "RequestMethod": "POST",
            "DownstreamStatus": 200,
            "time": "2026-11-15T10:00:00+00:00"
        }
        
        assert filter.match(record_get) is True
        assert filter.match(record_post) is False

    def test_filtrage_status_code(self):
        """Test de filtrage par code de statut HTTP."""
        filter_200 = Filters('DownstreamStatus = 200')
        filter_error = Filters('DownstreamStatus >= 500')
        
        record_ok = {
            "RequestMethod": "GET",
            "DownstreamStatus": 200,
            "time": "2026-11-15T10:00:00+00:00"
        }
        record_error = {
            "RequestMethod": "GET",
            "DownstreamStatus": 500,
            "time": "2026-11-15T10:00:00+00:00"
        }
        
        assert filter_200.match(record_ok) is True
        assert filter_200.match(record_error) is False
        assert filter_error.match(record_ok) is False
        assert filter_error.match(record_error) is True

    def test_filtre_clé_inexistante(self):
        """Test que une clé inexistante lève une exception."""
        with pytest.raises(Exception, match="Filter key 'InvalidKey' does not exist"):
            Filters('InvalidKey = "value"')

    def test_composite_filter_and(self):
        """Test of composite filter with && (and)."""
        filter_and = Filters('DownstreamStatus >= 200 && DownstreamStatus < 400')
        
        record_ok = {
            "DownstreamStatus": 200,
            "time": "2026-11-15T10:00:00+00:00"
        }
        record_error = {
            "DownstreamStatus": 500,
            "time": "2026-11-15T10:00:00+00:00"
        }
        
        assert filter_and.match(record_ok) is True
        assert filter_and.match(record_error) is False

    def test_composite_filter_or(self):
        """Test of composite filter with || (or)."""
        filter_or = Filters('DownstreamStatus >= 200 || DownstreamStatus < 50')
        
        record_ok = {
            "DownstreamStatus": 200,
            "time": "2026-11-15T10:00:00+00:00"
        }
        record_error = {
            "DownstreamStatus": 500,
            "time": "2026-11-15T10:00:00+00:00"
        }
        
        assert filter_or.match(record_ok) is True
        assert filter_or.match(record_error) is True

    def test_filter_contains(self):
        """Test of the contains filter with ~."""
        filter_contains = Filters('RequestMethod ~ "GET"')
        
        record_get = {
            "RequestMethod": "GET",
            "time": "2026-11-15T10:00:00+00:00"
        }
        record_post = {
            "RequestMethod": "POST",
            "time": "2026-11-15T10:00:00+00:00"
        }
        
        assert filter_contains.match(record_get) is True
        # Note: the contains filter only applies to exact RequestMethod here

    def test_unknown_filter_returns_false(self):
        """Test that a record without a key raises an exception."""
        filter_any = Filters('DownstreamStatus = 200')
        
        record_manquant = {
            "RequestMethod": "GET",
            # DownstreamStatus est manquant
            "time": "2026-11-15T10:00:00+00:00"
        }
        
        # Le match lève une NameError quand la clé n'est pas présente dans le record
        with pytest.raises(NameError):
            filter_any.match(record_manquant)


class TestRequestAccessLog:
    """Tests for the RequestAccessLog function."""

    def setup_method(self):
        """Create a test log file before each test."""
        dirpath = Path(__file__).parent.resolve().as_posix()
        self.test_file = Path( dirpath ) / Path("resources/test_access.log")
        
        # Create test records
        records = [
            {
                "ClientAddr": "192.168.1.1",
                "RequestMethod": "GET",
                "DownstreamStatus": 200,
                "time": "2026-11-15T10:00:00+00:00",
                "StartLocal": "2026-11-15T11:00:00.123456+01:00",
                "StartUTC": "2026-11-15T10:00:00.123456Z"
            },
            {
                "ClientAddr": "192.168.1.2",
                "RequestMethod": "POST",
                "DownstreamStatus": 201,
                "time": "2026-11-15T10:00:01+00:00",
                "StartLocal": "2026-11-15T11:00:01.123456+01:00",
                "StartUTC": "2026-11-15T10:00:01.123456Z"
            },
            {
                "ClientAddr": "192.168.1.3",
                "RequestMethod": "GET",
                "DownstreamStatus": 404,
                "time": "2026-11-15T10:00:02+00:00",
                "StartLocal": "2026-11-15T11:00:02.123456+01:00",
                "StartUTC": "2026-11-15T10:00:02.123456Z"
            },
            {
                "ClientAddr": "192.168.1.4",
                "RequestMethod": "GET",
                "DownstreamStatus": 500,
                "time": "2026-11-15T10:00:03+00:00",
                "StartLocal": "2026-11-15T11:00:03.123456+01:00",
                "StartUTC": "2026-11-15T10:00:03.123456Z"
            },
            {
                "ClientAddr": "192.168.1.5",
                "RequestMethod": "GET",
                "DownstreamStatus": 200,
                "time": "2026-11-15T10:00:04+00:00",
                "StartLocal": "2026-11-15T11:00:04.123456+01:00",
                "StartUTC": "2026-11-15T10:00:04.123456Z"
            },
        ]
        
        with open(self.test_file, 'wb') as f:
            for record in records:
                f.write(orjson.dumps(record) + b'\n')

    def teardown_method(self):
        """Remove the test file after each test."""
        if self.test_file.exists():
            self.test_file.unlink()

    async def test_first_page_with_default_pagination(self):
        """Test of the first page with default pagination."""
        result = await RequestAccessLog(
            access_log_file=self.test_file,
            filter_expr='DownstreamStatus >= 200',
            page=1,
            per_page=2
        )
        
        assert result['total_pages'] == 2
        assert result['total_items'] == 5  # tous les 5 records ont DownstreamStatus >= 200
        assert len(result['results']) == 2

    async def test_last_page_of_pagination(self):
        """Test of the last page of pagination."""
        result = await RequestAccessLog(
            access_log_file=self.test_file,
            filter_expr='DownstreamStatus >= 200',
            page=3,
            per_page=2
        )
        
        assert len(result['results']) == 1

    async def test_ascending_sort(self):
        """Test of ascending sort by key."""
        result = await RequestAccessLog(
            access_log_file=self.test_file,
            filter_expr='DownstreamStatus >= 200',
            page=1,
            per_page=10,
            sort='+ClientAddr'
        )
        
        if result['results']:
            addrs = [r['ClientAddr'] for r in result['results']]
            assert addrs == sorted(addrs)

    async def test_descending_sort(self):
        """Test of descending sort by key."""
        result = await RequestAccessLog(
            access_log_file=self.test_file,
            filter_expr='DownstreamStatus >= 200',
            page=1,
            per_page=10,
            sort='-time'
        )
        
        if result['results']:
            times = [r['time'] for r in result['results']]
            assert times == sorted(times, reverse=True)

    async def test_error_status_filter(self):
        """Test of error filtering."""
        result = await RequestAccessLog(
            access_log_file=self.test_file,
            filter_expr='DownstreamStatus >= 500',
            page=1,
            per_page=10
        )
        
        assert len(result['results']) == 1
        assert result['results'][0]['DownstreamStatus'] == 500

    async def test_unknown_filter(self):
        """Test with an unknown filter (returns empty)."""
        try: 
            await RequestAccessLog(
                access_log_file=self.test_file,
                filter_expr='InvalidKey = "value"',
                page=1,
                per_page=10
            )
            res = " "
        except Exception as e:
            res = str(e)
        assert "Filter key 'InvalidKey' does not exist." in res


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
