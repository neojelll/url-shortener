import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
import asyncio

from kafka import KafkaProducer
import json

from urllib.parse import urlparse
from pydantic import BaseModel
import uuid


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Синий
        'INFO': '\033[92m',   # Зеленый
        'WARNING': '\033[93m',  # Желтый
        'ERROR': '\033[91m',  # Красный
        'CRITICAL': '\033[95m',  # Пурпурный
        'RESET': '\033[0m',   # Сброс цвета
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f'{color}{record.levelname}{self.COLORS["RESET"]}'
        return super().format(record)


logging.basicConfig(
    filename="api.log",
    encoding="utf-8",
    filemode="w",
    level=logging.DEBUG,
    format="{asctime}  [{name}]  {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )
logger = logging.getLogger(__name__)


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)


formatter = ColoredFormatter('%(levelname)s: %(message)s')
ch.setFormatter(formatter)


logger.addHandler(ch)


def is_valid_url(url: str) -> bool:
    logger.debug(f"Start is valid URL function...\nparams: {url}")
    try:
        parsed_url = urlparse(url)
        returned = bool(parsed_url.netloc)
        logger.debug(f"Is valid URL function completed.\nreturned: {returned}")
        return returned
    except Exception as error:
        logger.error(f"Is valid URL function error\nERROR INFO: {error}")
        raise error


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

        producer = KafkaProducer(
            bootstrap_service="localhost:9092",
            value_serializer=lambda x: json.dumps(x).encode("utf-8")
            )
        logger.debug(f"Send data to message-broker...\nparams: {request}")
        await producer.send("topic_name", request)
        producer.flush()
        producer.close()

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
    long_url = "http://github.com"
    logger.debug(f"Start redirect respondse...\nparams: {short_id}")
    #request to DB
    await asyncio.sleep(1)
    logger.debug(f"Redirect response completed.\nreturned: Redirect to {"long_url"}")
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
