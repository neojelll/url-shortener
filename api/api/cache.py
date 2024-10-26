from redis.asyncio import Redis
from api.logger import configure_logger
from loguru import logger
import os


configure_logger()


async def ttl():
    try:
        result = os.environ["CACHE_TTL"]
        return int(result)
    except Exception as e:
        logger.warning(f"CACHE_TTL environment variable error: {e}")
        return 3600


class Cache:
    def __init__(self):
        self.cache = Redis(host="localhost", port=6379, decode_responses=True)

    async def __aenter__(self):
        return self

    async def check(self, short_url):
        return await self.cache.get(short_url)

    async def set(self, short_url, long_url, expiration):
        try:
            await self.cache.set(short_url, long_url, ex=min(await ttl(), expiration))
            logger.debug("set to cache sucsessfully")
        except Exception as e:
            logger.error(f"Error when set in cache: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cache.aclose()
