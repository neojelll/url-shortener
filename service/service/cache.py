from redis.asyncio import Redis
from .logger import configure_logger
from loguru import logger
import os


configure_logger()


async def ttl():
    try:
        result = os.environ["CACHE_TTL"]
        logger.debug("successfully obtained the value of the environment variable")
        return int(result)
    except Exception as e:
        logger.warning(f"CACHE_TTL environment variable error: {e}")
        return 3600


class Cache:
    def __init__(self):
        self.session = Redis(
            host=os.environ["CACHE_HOST"],
            port=int(os.environ["CACHE_PORT"]),
            decode_responses=True,
        )

    async def __aenter__(self):
        return self

    async def create_recording(self, short_url, long_url, expiration):
        try:
            ttl_value = min(expiration * 3600, await ttl())
            logger.debug(f"Start cache set func with: {short_url, long_url, ttl_value}")
            await self.session.set(short_url, long_url, ex=ttl_value)
            logger.info("write successfully to cache")
        except Exception as e:
            logger.error(f"Error when writing data to the cache: {e}")

    async def check_short_url(self, short_url):
        try:
            logger.debug(f"Start cache exists func with {short_url}")
            exists = await self.session.exists(short_url)
            if exists:
                logger.info(f"Short_url '{short_url}' exists in cache")
            else:
                logger.info(f"Short_url '{short_url}' does not exists in cache")
            return exists
        except Exception as e:
            logger.error(f"Error when cheking short_url in cache: {e}")
            return False

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.aclose()
