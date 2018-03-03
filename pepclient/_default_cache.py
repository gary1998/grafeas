import time
from cachetools import LRUCache


class DefaultCache(object):
    """
    PEP client cache with custom ttl per item built on cachetools.LRUCache
    """
    def __init__(self, maxsize=10000000, lru_cache_args={}):
        """
        maxsize - max size of cache as sent to cachetools.LRUCache (by default
                  this is the total size reported by sys.getsizeof on all the
                  items in the cache)
        """
        self._cache = LRUCache(maxsize, **lru_cache_args)
        self.hits = 0

    def set(self, key, allowed, ttl_seconds):
        """
        key - the cache key (string)
        allowed - a boolean value to store in the cache
        ttl_seconds - number of seconds to keep the value in the cache
        """
        assert isinstance(allowed, bool)
        self._cache[key] = (time.time() + ttl_seconds, allowed)

    def get(self, key):
        """
        key - the cache key (string)
        Returns a boolean if the key is in the cache, or None if the key is not
        in the cache.
        """
        item = self._cache.get(key)
        if item is None:
            return None
        else:
            exp, allowed = item
            if time.time() > exp:
                del self._cache[key]
                return None
            else:
                self.hits += 1
                return allowed

    def flush(self):
        """
        Delete all keys from this cache.
        This is only needed for testing.
        """
        self.hits = 0
        self._cache.clear()