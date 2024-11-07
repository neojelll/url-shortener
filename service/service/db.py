from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from .models import ShortUrl, LongUrl, UrlMapping
from sqlalchemy.future import select
from sqlalchemy import func
from .logger import configure_logger
from loguru import logger
import os


configure_logger()


class DataBase:
    def __init__(self):
        database_url = f"postgresql+asyncpg://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}"
        self.async_engine = create_async_engine(database_url, echo=True, future=True)
        self.async_session = async_sessionmaker(
            bind=self.async_engine, class_=AsyncSession, expire_on_commit=False
        )

    async def __aenter__(self):
        self.session = self.async_session()
        return self

    async def create_recording(self, short_url, long_url, expiration):
        try:
            logger.debug("add new tables in db...")
            new_long_url = LongUrl(long_value=long_url)
            new_short_url = ShortUrl(short_value=short_url)
            self.session.add(new_long_url)
            self.session.add(new_short_url)
            await self.session.commit()
            new_url_mapping = UrlMapping(
                long_id=new_long_url.long_id,
                short_id=new_short_url.short_id,
                expiration=expiration,
                date=func.now(),
            )
            self.session.add(new_url_mapping)
            await self.session.commit()
            logger.info(
                f"New long URL created: {new_long_url.long_value} with ID: {new_long_url.long_id}"
            )
            logger.info(
                f"New short URL created: {new_short_url.short_value} with ID: {new_short_url.short_id}"
            )
            logger.info(
                f"New UrlMapping created with long ID: {new_long_url.long_id} and short ID: {new_short_url.short_id}"
            )
        except Exception as e:
            logger.error(f"Error when writing data to the DB: {e}")

    async def check_short_url(self, short_value):
        try:
            logger.debug(f"select a short_url from a short_url: {short_value}")
            result = await self.session.execute(
                select(ShortUrl).where(ShortUrl.short_value == short_value)
            )
            short_url = result.scalars().first()
            if short_url is not None:
                logger.info(f"Short_url '{short_value}' exists in db")
            else:
                logger.info(f"Short_url '{short_value}' does not exists in db")
            return short_url
        except Exception as e:
            logger.error(f"Error when checking short_url from db: {e}")
            return None

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.aclose()
