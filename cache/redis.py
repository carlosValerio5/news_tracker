"""Redis Cache Service Module"""

import redis
import json
from dataclasses import asdict
from datetime import datetime
from logging import getLogger
from typing import TypeVar, Type, Union

from exceptions.cache_exceptions import CacheMissError

T = TypeVar("T")


class RedisService:
    """Service for interacting with Redis cache."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str = None,
        cache_prefix: str = "news_tracker",
        logger: object = None,
    ) -> None:
        """
        Initialize the Redis client.

        :param host: Redis server host.
        :param port: Redis server port.
        :param password: Password for Redis server if authentication is enabled.
        :param cache_prefix: Prefix for all cache keys to avoid collisions.
        :param logger: Logger instance for logging (optional).
        """
        self._redis_client = redis.Redis(
            host=host, port=port, password=password, decode_responses=True
        )
        self._cache_prefix = cache_prefix
        self._logger = logger if logger else self._set_logger()

    def _set_logger(self):
        """Get the logger instance."""
        try:
            logger = getLogger(__name__)
            return logger
        except Exception as e:
            raise Exception(f"Error initializing logger: {e}")

    def set_value(self, key: str, value: str, expire_seconds: int = 86400) -> None:
        """
        Set a value in the Redis cache.

        :param key: Key under which the value is stored.
        :param value: Value to store.
        :param expire_seconds: Optional expiration time in seconds.
        """
        self._redis_client.set(name=key, value=value, ex=expire_seconds)

    def get_value(self, key: str) -> str:
        """
        Get a value from the Redis cache.

        :param key: Key whose value is to be retrieved.
        :return: The value associated with the key or None if the key does not exist.
        """
        return self._redis_client.get(name=key)

    def delete_value(self, key: str) -> None:
        """
        Delete a value from the Redis cache.

        :param key: Key whose value is to be deleted.
        """
        self._redis_client.delete(key)

    def _get_cache_key(self, key: str, date: datetime) -> str:
        """
        Get the full cache key with prefix.

        :param key: The original key.
        :param date: The date to append to the key.
        :return: The full cache key with prefix.
        """
        date = date.strftime("%Y-%m-%d")
        return f"{self._cache_prefix}:{key}:{date}"

    def set_cached_data(
        self,
        key: str,
        date: datetime,
        data: Union[T, list[T]],
        expire_seconds: int = 86400,
    ) -> None:
        """
        Store one or more dataclass objects in the Redis cache with a date-based key.

        :param key: The cache key identifier.
        :param date: The date to include in the cache key.
        :param data: A single dataclass instance or a list of dataclass instances to serialize and cache.
        :param expire_seconds: TTL in seconds (default: 24 hours).
        """
        cache_key = self._get_cache_key(key, date)
        try:
            # Normalize to list for consistent serialization
            items = data if isinstance(data, list) else [data]
            # Convert each dataclass to dict
            data_dicts = [asdict(item) for item in items]
            serialized = json.dumps(data_dicts, default=str)
            self.set_value(cache_key, serialized, expire_seconds=expire_seconds)
            self._logger.debug(
                f"Successfully cached {len(items)} item(s) for key: {cache_key}"
            )
        except TypeError as e:
            self._logger.error(
                f"Error serializing data for key: {cache_key}, error: {e}"
            )
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error caching data for key: {cache_key}, error: {e}"
            )
            raise

    def get_cached_data(
        self, key: str, date: datetime, return_schema: Type[T]
    ) -> list[T]:
        """
        Retrieve cached data for a specific key and date and deserialize into dataclass instances.

        :param key: The cache key identifier.
        :param date: The date for which to retrieve the cached data.
        :param return_schema: A dataclass type to instantiate from cached dicts.
        :return: List of dataclass instances.
        :raises CacheMissError: If no cached data is found for the given key and date.
        """
        cache_key = self._get_cache_key(key, date)
        try:
            cached_data = self.get_value(cache_key)
            if cached_data:
                cached_list = json.loads(cached_data)
                items = cached_list if isinstance(cached_list, list) else [cached_list]
                return [
                    return_schema(**item)
                    if isinstance(item, dict)
                    else return_schema(item)
                    for item in items
                ]  # type: ignore
        except json.JSONDecodeError as e:
            raise CacheMissError(
                f"Error decoding cached data for key: {cache_key}, error: {e}"
            )
        except Exception as e:
            self._logger.error(
                f"Unexpected error retrieving cached data for key: {cache_key}, error: {e}"
            )
            raise

        if not cached_data:
            raise CacheMissError(f"No cached data found for key: {cache_key}")
