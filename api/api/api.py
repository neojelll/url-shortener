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
        logger.debug(f"Start send_data to kafka: {repr(data)}")
        await broker.send_data(data)

    logger.debug(f"Post request completed. returned: {repr(returned_value)}")
    return returned_value


@app.get("/v1/url/shorten")
async def get_request(short_url):
    logger.debug(f"Start get request... params: {short_url}")
    async with Cache() as cache:
        logger.debug(f"Start cache check func with: {short_url}")
        check = await cache.check(short_url)

        if check is not None:
            logger.debug("Cache is not None")
            long_url = check
        else:
            logger.debug("Cache is None")
            async with DataBase() as database:
                logger.debug(f"Start db get_long_url func with: {short_url}")
                long_url = await database.get_long_url(short_url)
                logger.debug(f"Start db get_expiration func with: {short_url}")
                expiration = await database.get_expiration(short_url)

            if long_url is None or expiration is None:
                logger.debug("long_url or expiration is None")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="URL is not found"
                )
            logger.debug("long_url or expiration is not None")
            logger.debug(f"Start cache set func with: {long_url}, {expiration}")
            await cache.set(short_url, long_url, expiration)
    returned_value = {"long_url": f"{long_url}"}
    logger.debug(f"get request completed. returned: {repr(returned_value)}")
    return returned_value


@app.get("/{short_url}")
async def redirect_request(short_url: str):
    logger.debug(f"Start redirect response... params: {repr(short_url)}")

    async with Cache() as cache:
        logger.debug(f"Start cache check func with: {short_url}")
        check = await cache.check(short_url)

        if check is not None:
            logger.debug("Cache is not None")
            long_url = check
        else:
            async with DataBase() as database:
                logger.debug(f"Start db get_long_url func with: {short_url}")
                long_url = await database.get_long_url(short_url)
                logger.debug(f"Start db get_expiration func with: {short_url}")
                expiration = await database.get_expiration(short_url)

            if long_url is None or expiration is None:
                logger.debug("long_url or expiration is None")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="URL is not valid"
                )
            logger.debug("long_url or expiration is not None")
            logger.debug(f"Start cache set func with: {long_url}, {expiration}")
            await cache.set(short_url, long_url, expiration)

    logger.debug(f"Redirect response completed. returned: Redirect to {repr(long_url)}")
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)  # type: ignore
