from loguru import logger
import sys

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from kafka import KafkaProducer
import json

from urllib.parse import urlparse
from pydantic import BaseModel
import uuid

from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import redis


logger.remove()


logger.add(sys.stderr, format="{time:YYYY-MM-DD at HH:mm:ss} <level>{level}</level> <red>{name}</red>: <red>{function}</red>({line}) - <cyan>{message}</cyan>", level="DEBUG")


logger.add("api.log", format="{time:YYYY-MM-DD at HH:mm:ss} {level} {name}: {function}({line}) - {message}", level="DEBUG")


USERNAME = 'your_username'
PASSWORD = 'your_password'
HOST = 'remote_host_address'
PORT = '5432'
DATABASE = 'your_database_name'


DATABASE_URL = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'


Base = declarative_base()

# Определяем модель LongUrl
class LongUrl(Base):
    __tablename__ = 'long_url'

    long_id = Column(Integer, primary_key=True)
    long_value = Column(Text, unique=True, nullable=False)

# Определяем модель ShortUrl
class ShortUrl(Base):
    __tablename__ = 'short_url'

    short_id = Column(String(20), primary_key=True)
    short_value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)

# Определяем модель UrlMapping
class UrlMapping(Base):
    __tablename__ = 'url_mapping'

    short_id = Column(String(20), ForeignKey('short_url.short_id'), primary_key=True)
    long_id = Column(Integer, ForeignKey('long_url.long_id'), nullable=False)
    expiration_date = Column(TIMESTAMP)

    short_url = relationship('ShortUrl', backref='url_mappings')
    long_url = relationship('LongUrl', backref='url_mappings')


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
async def post_url(request: ShortURLRequest):
    logger.debug(f"Start post request... params: {repr(request)}")
    url = request.url
    if not is_valid_url(url):
        logger.error("Post request error. ERROR INFO: Invalid URL")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid URL")
    task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
    returned_value = {"task": str(task_num)}

    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda x: json.dumps(x).encode("utf-8")
        )
    logger.debug(f"Send data to message-broker... params: {repr(request)}")
    await producer.send("topic_name", request)
    producer.flush()
    producer.close()

    logger.debug(f"Post request completed. returned: {repr(returned_value)}")
    return returned_value


@app.get("/v1/url/shorten")
async def get_request():
    pass


@app.get("/{short_url}")
async def transport_to_long_url(short_url: str):
    logger.debug(f"Start redirect response... params: {repr(short_url)}")

    cache = redis.Redis(
    host='localhost',
    port=6379,
    db=0,# Номер базы данных (по умолчанию 0)
    decode_responses=True# Автоматически декодировать байтовые строки в строки
    )

    if cache.exists(short_url):
        long_url = cache.get(short_url)
    else:
        engine = create_engine(DATABASE_URL)

        Session = sessionmaker(bind=engine)
        session = Session()
        def get_long_value(short_value):
            result = (
        		session.query(LongUrl)
        		.join(UrlMapping)
        		.join(ShortUrl)
        		.filter(ShortUrl.short_value == short_value)
        		.first()
    		)
            return result.long_value if result else None

        long_url = get_long_value(short_value=short_url)
        session.close()

    cache.set(short_url, long_url) #type: ignore

    logger.debug(f"Redirect response completed. returned: Redirect to {repr("long_url")}")
    return RedirectResponse(url="http://github.com", status_code=status.HTTP_302_FOUND) #type: ignore