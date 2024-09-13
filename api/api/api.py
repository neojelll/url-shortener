import logging

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import asyncio

from urllib.parse import urlparse
from pydantic import BaseModel
import uuid


logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime}  [{name}]  {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )
logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)
    return bool(parsed_url.netloc)


class ShortURLRequest(BaseModel):
    url: str
    prefix: str = ""
    expiration: int = 24


app = FastAPI(title="URL Shortener API")


@app.post("/v1/url/shorten")
async def post_url(request: ShortURLRequest):
    logger.debug(f"Start post request...\nparams: {request}")
    url = request.url
    if is_valid_url(url):
        task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
        returned_value = {"task": str(task_num)}
        #send data to kafka
        logger.debug(f"Send data to kafka...\nparams: {request}")
        await asyncio.sleep(1)
        logger.debug(f"Post request completed.\nreturned: {returned_value}")
        return returned_value
    logger.error("Post request error.\nERROR INFO: Invalid URL")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid URL")


@app.get("/v1/url/shorten")
async def get_request():
    pass


@app.get("/{short_id}")
async def transport_to_long_url(short_id: str):
    logger.debug(f"Start redirect respondse...\nparams: {short_id}")
    #request to DB
    await asyncio.sleep(1)
    logger.debug(f"Redirect response completed.\nreturned: Redirect to {"long_url"}")
    return RedirectResponse(url="long_url", status_code=status.HTTP_302_FOUND)
