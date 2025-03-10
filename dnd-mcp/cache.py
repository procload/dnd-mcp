from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
import logging
import json
import os
import pickle

logger = logging.getLogger(__name__)


class APICache:
    """A time-based cache for API responses with optional persistence."""

    def __init__(self, ttl_hours: int = 24, persistent: bool = True, cache_dir: str = "cache"):
        """Initialize the cache with a specified TTL (time-to-live).

        Args:
            ttl_hours: Number of hours before cached items expire
            persistent: Whether to persist the cache to disk
            cache_dir: Directory to store persistent cache files
        """
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.persistent = persistent
        self.cache_dir = cache_dir

        if self.persistent:
            os.makedirs(self.cache_dir, exist_ok=True)
            self._load_cache()

        logger.debug(
            f"Initialized API cache with TTL of {ttl_hours} hours (persistent: {persistent})")

    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key.

        Args:
            key: The cache key

        Returns:
            The file path for the cache key
        """
        # Convert the key to a valid filename
        filename = key.replace("/", "_").replace(":", "_")
        return os.path.join(self.cache_dir, f"{filename}.pickle")

    def _load_cache(self) -> None:
        """Load the cache from disk."""
        try:
            # Load the cache index if it exists
            index_path = os.path.join(self.cache_dir, "index.json")
            if os.path.exists(index_path):
                with open(index_path, "r") as f:
                    index = json.load(f)

                # Load each cache item
                for key, timestamp_str in index.items():
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if datetime.now() - timestamp < self.ttl:
                        cache_path = self._get_cache_path(key)
                        if os.path.exists(cache_path):
                            try:
                                with open(cache_path, "rb") as f:
                                    value = pickle.load(f)
                                    self.cache[key] = (value, timestamp)
                            except Exception as e:
                                logger.warning(
                                    f"Failed to load cache item {key}: {e}")

                logger.info(
                    f"Loaded {len(self.cache)} items from persistent cache")
        except Exception as e:
            logger.warning(f"Failed to load cache from disk: {e}")

    def _save_cache_item(self, key: str, value: Any, timestamp: datetime) -> None:
        """Save a cache item to disk.

        Args:
            key: The cache key
            value: The value to cache
            timestamp: The timestamp when the item was cached
        """
        if not self.persistent:
            return

        try:
            # Save the cache item
            cache_path = self._get_cache_path(key)
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)

            # Update the cache index
            index_path = os.path.join(self.cache_dir, "index.json")
            index = {}
            if os.path.exists(index_path):
                try:
                    with open(index_path, "r") as f:
                        index = json.load(f)
                except Exception:
                    pass

            index[key] = timestamp.isoformat()

            with open(index_path, "w") as f:
                json.dump(index, f)
        except Exception as e:
            logger.warning(f"Failed to save cache item {key} to disk: {e}")

    def get(self, key: str) -> Any:
        """Get a value from the cache if it exists and is not expired.

        Args:
            key: The cache key to retrieve

        Returns:
            The cached value or None if not found or expired
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                logger.debug(f"Cache expired for key: {key}")
        else:
            logger.debug(f"Cache miss for key: {key}")
        return None

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache with the current timestamp.

        Args:
            key: The cache key
            value: The value to cache
        """
        timestamp = datetime.now()
        self.cache[key] = (value, timestamp)
        logger.debug(f"Cached value for key: {key}")

        if self.persistent:
            self._save_cache_item(key, value, timestamp)

    def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()
        logger.debug("Cache cleared")

        if self.persistent:
            try:
                # Clear the cache directory
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                logger.debug("Persistent cache cleared")
            except Exception as e:
                logger.warning(f"Failed to clear persistent cache: {e}")

    def __len__(self) -> int:
        """Return the number of items in the cache."""
        return len(self.cache)
