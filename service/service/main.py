from .message_broker import MessageBroker
from .shortener_service import check_short_url
from .logger import configure_logger
from loguru import logger
from .db import DataBase
from .cache import Cache
import asyncio
import json


configure_logger()


async def main() -> None:
    async with MessageBroker() as broker:
        async for message in broker.consume_data():
            logger.debug("Start cunsume data with kafka")
            data = json.loads(message)
            long_url = data["url"]
            expiration = data["expiration"]
            short_url = await check_short_url(data["prefix"])
            async with Cache() as cache:
                logger.debug(
                    f"Start cache func create_recoring with: {short_url, long_url, expiration}"
                )
                await cache.create_recording(short_url, long_url, expiration)
            async with DataBase() as db:
                logger.debug(
                    f"Start db func create_recoring with: {short_url, long_url, expiration}"
                )
                await db.create_recording(short_url, long_url, expiration)


def run() -> None:
    asyncio.run(main())
