from asyncio import Lock
from collections import OrderedDict
from typing import Any

class Cache:
    """
    An asynchronous, thread-safe cache implementation using an OrderedDict.
    Supports LRU (Least Recently Used) eviction policy when the maximum size is exceeded.

    Attributes:
        max_size (``int``): Maximum number of items the cache can hold. Default is 10.

    Private Attributes:
        _store (``OrderedDict``): Underlying storage for the cache.
        _lock (``Lock``): Asyncio lock for thread-safe operations.
    """
    __slots__ = ('_store', 'max_size', '_lock')

    def __init__(self, max_size: int = 10) -> None:
        """
        Initializes the cache with a maximum size.

        Args:
            max_size (``int``): Maximum number of items the cache can hold. Default is 10.
        """
        self._store: OrderedDict = OrderedDict()
        self._lock: Lock = Lock()
        self.max_size: int = max_size

    def __repr__(self) -> str:
        """
        Returns a string representation of the cache, including max size and current size.

        Returns:
            ``str``: String representation of the cache.
        """
        return f'{__class__.__name__}\
            (max_size={self.max_size},\
            current_size={self.__len__()})'

    def __len__(self) -> int:
        """
        Returns the number of items in the cache.

        Returns:
            ``int``: Current size of the cache.
        """
        return len(self._store)
    
    async def __contains__(self, key: str) -> bool:
        """
        Checks if a key exists in the cache.

        Args:
            key (``str``): Key to check.

        Returns:
            ``bool``: True if the key exists, False otherwise.
        """
        return await self.has(key)

    async def _update_key(self, key: str) -> None:
        """
        Moves a key to the end of the cache to mark it as recently used.

        Args:
            key (``str``): Key to update.
        """
        if key in self._store:
            self._store.move_to_end(key)

    async def set(self, key: str, value: Any) -> None:
        """
        Adds a key-value pair to the cache. Evicts the least recently used item if the cache is full.

        Args:
            key (``str``): Key to add.
            value (``Any``): Value to associate with the key.
        """
        async with self._lock:
            await self._update_key(key)
            self._store[key] = value

            if len(self._store) > self.max_size:
                self._store.popitem(last=False)

    async def get(self, key: str) -> Any :
        """
        Retrieves the value associated with a key from the cache.

        Args:
            key (``str``): Key to retrieve.

        Returns:
            ``Any``: Value associated with the key, or None if the key doesn't exist.
        """
        async with self._lock:
            await self._update_key(key)
            return self._store.get(key)

    async def delete(self, key: str) -> None:
        """
        Removes a key-value pair from the cache.

        Args:
            key (``str``): Key to delete.
        """
        async with self._lock:
            self._store.pop(key, None)

    async def has(self, key: str) -> bool:
        """
        Checks if a key exists in the cache.

        Args:
            key (``str``): Key to check.

        Returns:
            ``bool``: True if the key exists, False otherwise.
        """
        async with self._lock:
            return key in self._store

    async def clear(self) -> None:
        """
        Clears all items from the cache.
        """
        async with self._lock:
            self._store.clear()

    async def keys(self) -> list[str]:
        """
        Retrieves all keys currently in the cache.

        Returns:
            ``list[str]``: List of keys in the cache.
        """
        async with self._lock:
            return list(self._store.keys())