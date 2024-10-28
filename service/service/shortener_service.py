from .db import DataBase
from .cache import Cache
from .logger import configure_logger
from loguru import logger
import string
import random


configure_logger()


async def generate_random_string(length=7):
    logger.debug(f"start generate_random_string params: {length}")
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    logger.debug(f"generate_random_string completed return value: {random_string}")
    return random_string


async def shortener(prefix: str) -> str:
    if prefix:
        random_string = await generate_random_string(4)
        short_url = f"{prefix}/{random_string}"
    else:
        random_string = await generate_random_string(7)
        short_url = random_string
    logger.debug(f"create short_url completed return value: {short_url}")
    return short_url


async def check_short_url(prefix=""):
    logger.debug(f"Start check_short_url params: {prefix}")
    short_url = await shortener(prefix)
    async with Cache() as cache:
        if await cache.check_short_url(short_url):
            logger.debug("start shortener two, search in cache")
            short_url = await shortener(prefix)
        else:
            async with DataBase() as db:
                if await db.check_short_url(short_url) is not None:
                    logger.debug("start shortener two, search in db")
                    short_url = await shortener(prefix)
    logger.debug(f"check_short_url completed return value: {short_url}")
    return short_url
