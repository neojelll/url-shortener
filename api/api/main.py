from loguru import logger
from .api import app
import asyncio
import uvicorn


async def main() -> None:
    logger.info("Starting the server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


def run() -> None:
    asyncio.run(main())
