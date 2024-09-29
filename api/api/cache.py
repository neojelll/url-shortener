from redis import Redis
import os


def ttl():
    result = os.environ["CACHE_TTL"]
    return int(result)


class Cache(object):
    def __init__(self):
        self.cache = Redis(host="localhost", port=6379, db=0, decode_responses=True)

    async def __aenter__(self):
        return self

    async def check(self, short_url):
        return await self.cache.get(short_url)

    async def set(self, short_url, long_url, expiration):
        await self.cache.set(short_url, long_url, ex=min(ttl(), expiration))

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cache.close()  # type: ignore
