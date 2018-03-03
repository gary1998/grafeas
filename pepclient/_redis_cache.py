class PEPRedisCache(object):
    def __init__(self, host='localhost', port=6379, db_index=0):
        # Import here so people can use this library without installing
        # the redis python package.
        import redis
        self._client = redis.StrictRedis(
            host=host,
            port=port,
            db=db_index,
        )
        self.hits = 0

    def set(self, key, allowed, ttl_seconds):
        """
        key - the cache key (string)
        allowed - a boolean value to store in the cache
        ttl_seconds - number of seconds to keep the value in the cache
        """
        assert isinstance(allowed, bool)
        self._client.set(key, str(allowed), ex=ttl_seconds)

    def get(self, key):
        """
        key - the cache key (string)
        Returns a boolean if the key is in the cache, or None if the key is not
        in the cache.
        """
        value = self._client.get(key)
        if value is None:
            return None
        else:
            self.hits += 1
            return value == 'True'

    def flush(self):
        """
        Delete all keys from this cache.
        This is only needed for testing-.
        """
        self.hits = 0
        self._client.flushdb()