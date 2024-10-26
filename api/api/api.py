from .logger import configure_logger
from loguru import logger

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from .message_broker import MessageBroker
from .db import DataBase
from .cache import Cache

from urllib.parse import urlparse
from pydantic import BaseModel
import uuid


configure_logger()


def is_valid_url(url: str) -> bool:
    logger.debug(f"Start is valid URL function... params: {repr(url)}")
    parsed_url = urlparse(url)
    returned = bool(parsed_url.netloc)
    logger.debug(f"Is valid URL function completed. returned: {repr(returned)}")
    return returned


class ShortURLRequest(BaseModel):
    url: str
    prefix: str = ""
    expiration: int = 24


app = FastAPI(title="URL Shortener API")


@app.post("/v1/url/shorten")
async def post_url(data: ShortURLRequest):
    logger.debug(f"Start post request... params: {repr(data)}")
    url = data.url
    if not is_valid_url(url):
        logger.error("Post request error. ERROR INFO: Invalid URL")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL"
        )
    task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
    returned_value = {"task": str(task_num)}

    async with MessageBroker() as broker:
        await broker.send_data("my_topic", data)

    logger.debug(f"Post request completed. returned: {repr(returned_value)}")
    return returned_value


@app.get("/v1/url/shorten")
async def get_request(short_url):
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
                    status_code=status.HTTP_404_NOT_FOUND, detail="URL is not found"
                )
            await cache.set(short_url, long_url, expiration)
    return {"long_url": f"{long_url}"}


@app.get("/{short_url}")
async def redirect_request(short_url: str):
    logger.debug(f"Start redirect response... params: {repr(short_url)}")

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

    logger.debug(f"Redirect response completed. returned: Redirect to {repr(long_url)}")
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)  # type: ignore
