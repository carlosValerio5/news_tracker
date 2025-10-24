import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime
from dataclasses import dataclass
from cache.redis import RedisService
from exceptions.cache import CacheMissError


@dataclass
class MockedData:
    id: str
    name: str
    value: int


class TestRedisService:
    """Test suite for RedisService class."""

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for testing."""
        return MagicMock()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing."""
        return MagicMock()

    @pytest.fixture
    def redis_service(self, mock_redis_client, mock_logger):
        """RedisService instance with mocked dependencies."""
        with patch("cache.redis.redis.Redis", return_value=mock_redis_client):
            service = RedisService(
                host="localhost", port=6379, password="test", logger=mock_logger
            )
            return service

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        with patch("cache.redis.getLogger", return_value=MagicMock()):
            with patch("cache.redis.redis.Redis") as mock_redis_class:
                service = RedisService()

        assert service._cache_prefix == "news_tracker"
        mock_redis_class.assert_called_once_with(
            host="localhost",
            port=6379,
            password=None,
            ssl=True,
            ssl_cert_reqs=None,
            ssl_ca_certs=None,
            ssl_check_hostname=False,
            socket_timeout=5,
            socket_connect_timeout=5,
            socket_keepalive=True,
            socket_keepalive_options={},
            retry_on_timeout=True,
            health_check_interval=30,
            decode_responses=True
        )

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        with patch("cache.redis.redis.Redis") as mock_redis_class:
            service = RedisService(
                host="custom.host",
                port=6380,
                password="secret",
                cache_prefix="custom_prefix",
                logger=MagicMock(),
            )

        assert service._cache_prefix == "custom_prefix"
        mock_redis_class.assert_called_once_with(
            host="custom.host", 
            port=6380, 
            password="secret", 
            ssl=True,
            ssl_cert_reqs=None,
            ssl_ca_certs=None,
            ssl_check_hostname=False,
            socket_timeout=5,
            socket_connect_timeout=5,
            socket_keepalive=True,
            socket_keepalive_options={},
            retry_on_timeout=True,
            health_check_interval=30,
            decode_responses=True
        )

    def test_init_logger_error(self):
        """Test initialization when logger setup fails."""
        with patch("cache.redis.redis.Redis"):
            with patch("cache.redis.getLogger", side_effect=Exception("Logger error")):
                with pytest.raises(Exception, match="Error initializing logger"):
                    RedisService()

    def test_set_value(self, redis_service, mock_redis_client):
        """Test setting a value in Redis."""
        redis_service.set_value("test_key", "test_value", expire_seconds=3600)

        mock_redis_client.set.assert_called_once_with(
            name="test_key", value="test_value", ex=3600
        )

    def test_get_value(self, redis_service, mock_redis_client):
        """Test getting a value from Redis."""
        mock_redis_client.get.return_value = "test_value"

        result = redis_service.get_value("test_key")

        assert result == "test_value"
        mock_redis_client.get.assert_called_once_with(name="test_key")

    def test_delete_value(self, redis_service, mock_redis_client):
        """Test deleting a value from Redis."""
        redis_service.delete_value("test_key")

        mock_redis_client.delete.assert_called_once_with("test_key")

    def test_get_cache_key(self, redis_service):
        """Test cache key generation."""
        date = datetime(2025, 10, 20)
        key = redis_service._get_cache_key("test_key", date)

        assert key == "news_tracker:test_key:2025-10-20"

    def test_set_cached_data_single_item(
        self, redis_service, mock_redis_client, mock_logger
    ):
        """Test caching a single dataclass item."""
        test_item = MockedData(id="1", name="test", value=42)
        date = datetime(2025, 10, 20)

        redis_service.set_cached_data("test_key", date, test_item)

        # Verify the data was serialized and stored
        call_args = mock_redis_client.set.call_args
        stored_value = call_args[1]["value"]
        stored_data = json.loads(stored_value)

        assert len(stored_data) == 1
        assert stored_data[0]["id"] == "1"
        assert stored_data[0]["name"] == "test"
        assert stored_data[0]["value"] == 42

        # Verify expiration and key
        assert call_args[1]["ex"] == 86400
        assert call_args[1]["name"] == "news_tracker:test_key:2025-10-20"

        mock_logger.debug.assert_called_once()

    def test_set_cached_data_list_items(
        self, redis_service, mock_redis_client, mock_logger
    ):
        """Test caching a list of dataclass items."""
        test_items = [
            MockedData(id="1", name="test1", value=42),
            MockedData(id="2", name="test2", value=43),
        ]
        date = datetime(2025, 10, 20)

        redis_service.set_cached_data("test_key", date, test_items)

        call_args = mock_redis_client.set.call_args
        stored_value = call_args[1]["value"]
        stored_data = json.loads(stored_value)

        assert len(stored_data) == 2
        assert stored_data[0]["id"] == "1"
        assert stored_data[1]["id"] == "2"

        mock_logger.debug.assert_called_once()

    def test_set_cached_data_serialization_error(self, redis_service, mock_logger):
        """Test error handling during data serialization."""
        # Create an object that can't be serialized
        bad_item = object()
        date = datetime(2025, 10, 20)

        with pytest.raises(TypeError):
            redis_service.set_cached_data("test_key", date, bad_item)

        mock_logger.error.assert_called_once()

    def test_set_cached_data_unexpected_error(
        self, redis_service, mock_redis_client, mock_logger
    ):
        """Test unexpected error during caching."""
        mock_redis_client.set.side_effect = Exception("Redis error")
        test_item = MockedData(id="1", name="test", value=42)
        date = datetime(2025, 10, 20)

        with pytest.raises(Exception, match="Redis error"):
            redis_service.set_cached_data("test_key", date, test_item)

        mock_logger.error.assert_called_once()

    def test_get_cached_data_success(self, redis_service, mock_redis_client):
        """Test successful retrieval of cached data."""
        # Mock cached JSON data
        cached_json = json.dumps([{"id": "1", "name": "test", "value": 42}])
        mock_redis_client.get.return_value = cached_json

        date = datetime(2025, 10, 20)
        result = redis_service.get_cached_data("test_key", date, MockedData)

        assert len(result) == 1
        assert isinstance(result[0], MockedData)
        assert result[0].id == "1"
        assert result[0].name == "test"
        assert result[0].value == 42

    def test_get_cached_data_single_item_as_list(
        self, redis_service, mock_redis_client
    ):
        """Test retrieval when single item is stored as list."""
        cached_json = json.dumps({"id": "1", "name": "test", "value": 42})
        mock_redis_client.get.return_value = cached_json

        date = datetime(2025, 10, 20)
        result = redis_service.get_cached_data("test_key", date, MockedData)

        assert len(result) == 1
        assert isinstance(result[0], MockedData)

    def test_get_cached_data_cache_miss(self, redis_service, mock_redis_client):
        """Test cache miss when no data is found."""
        mock_redis_client.get.return_value = None

        date = datetime(2025, 10, 20)
        with pytest.raises(CacheMissError, match="No cached data found"):
            redis_service.get_cached_data("test_key", date, MockedData)

    def test_get_cached_data_json_decode_error(self, redis_service, mock_redis_client):
        """Test JSON decode error handling."""
        mock_redis_client.get.return_value = "invalid json"

        date = datetime(2025, 10, 20)
        with pytest.raises(CacheMissError, match="Error decoding cached data"):
            redis_service.get_cached_data("test_key", date, MockedData)

    def test_get_cached_data_unexpected_error(
        self, redis_service, mock_redis_client, mock_logger
    ):
        """Test unexpected error during cache retrieval."""
        mock_redis_client.get.side_effect = Exception("Redis connection error")

        date = datetime(2025, 10, 20)
        with pytest.raises(Exception, match="Redis connection error"):
            redis_service.get_cached_data("test_key", date, MockedData)

        mock_logger.error.assert_called_once()

    def test_get_cached_data_instantiation_error(
        self, redis_service, mock_redis_client
    ):
        """Test error when cached data doesn't match schema."""
        # Missing required field
        cached_json = json.dumps([{"id": "1", "name": "test"}])  # missing 'value'
        mock_redis_client.get.return_value = cached_json

        date = datetime(2025, 10, 20)
        with pytest.raises(TypeError):  # dataclass instantiation error
            redis_service.get_cached_data("test_key", date, MockedData)
