from .message_broker import MessageBroker
from .shortener_service import check_short_url
from .logger import configure_logger
from .db import DataBase
from .cache import Cache
import asyncio
import json


configure_logger()


async def main() -> None:
    async with MessageBroker() as broker:
        async for message in broker.consume_data():
            data = json.loads(message)
            long_url = data["url"]
            expiration = data["expiration"]
            short_url = await check_short_url(data["prefix"])
            async with Cache() as cache:
                await cache.create_recording(short_url, long_url, expiration)
            async with DataBase() as db:
                await db.create_recording(short_url, long_url, expiration)


def run() -> None:
    asyncio.run(main())
