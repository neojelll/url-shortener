from .db import DataBase
import asyncio


async def expiration_manager():
    async with DataBase() as db:
        rowcount = await db.delete_after_time()
    return rowcount


def run():
    asyncio.run(expiration_manager())
