from .logger import configure_logger
from loguru import logger

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from .message_broker import BrokerProducer, BrokerConsumer
from .db import DataBase
from .cache import Cache

from urllib.parse import urlparse
from pydantic import BaseModel
import uuid


configure_logger()


def is_valid_url(url: str) -> bool:
    logger.debug(f"Start is_valid_url, params: {repr(url)}")
    parsed_url = urlparse(url)
    returned = bool(parsed_url.netloc)
    logger.debug(f"Completed is_valid_url, returned: {repr(returned)}")
    return returned


class ShortURLRequest(BaseModel):
    url: str
    prefix: str = ""
    expiration: int = 24


app = FastAPI(title="URL Shortener API")


@app.post("/v1/url/shorten")
async def send_data(data: ShortURLRequest) -> dict[str, str]:
    logger.debug(f"Start send_data... params: {repr(data)}")
    long_url = data.url

    if not is_valid_url(long_url):
        logger.error("Error send_data: Invalid Url")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL"
        )

    task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(long_url).netloc)
    task = {"task": str(task_num)}

    data_dict: dict = data.model_dump()
    data_dict.update(task)
    logger.debug(f"data_dict: {data_dict}")

    async with BrokerProducer() as broker:
        await broker.send_data(data_dict)

    logger.debug(f"Completed send_data, returned: {repr(task)}")
    return task


@app.get("/v1/url/shorten")
async def get_short_url(task_num: str) -> dict[str, str]:
    logger.debug(f"Start get_short_url, params: {task_num}")
    async with BrokerConsumer() as broker:
        short_url = await broker.consume_data(task_num)
        if short_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL is not found"
            )
    return_value = {"short_url": f"{short_url}"}
    logger.debug(f"Completed get_short_url, returned: {repr(return_value)}")
    return return_value


@app.get("/{short_url}")
async def redirect_request(short_url: str) -> RedirectResponse:
    logger.debug(f"Start redirect_request, params: {repr(short_url)}")

    async with Cache() as cache:
        check = await cache.check(short_url)

        if check is not None:
            long_url = check
        else:
            async with DataBase() as database:
                long_url = await database.get_long_url(short_url)
                expiration = await database.get_expiration(short_url)

            if long_url is None or expiration is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="URL is not valid"
                )

            await cache.set(short_url, long_url, expiration)

    logger.debug(f"Completed redirect_request, returned: Redirect to {repr(long_url)}")
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
