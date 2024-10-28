from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs,
)
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import delete, func
from .logger import configure_logger
from loguru import logger
import os


configure_logger()


class Base(AsyncAttrs, DeclarativeBase):
    pass


class LongUrl(Base):
    __tablename__ = "long_url"
    long_id = Column(Integer, primary_key=True)
    long_value = Column(String(250), unique=True, nullable=False)


class ShortUrl(Base):
    __tablename__ = "short_url"
    short_id = Column(Integer, primary_key=True)
    short_value = Column(String(250), nullable=False)


class UrlMapping(Base):
    __tablename__ = "url_mapping"
    short_id = Column(Integer, ForeignKey("short_url.short_id"), primary_key=True)
    long_id = Column(Integer, ForeignKey("long_url.long_id"), nullable=False)
    expiration = Column(Integer, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    short_url = relationship("ShortUrl", backref="url_mappings")
    long_url = relationship("LongUrl", backref="url_mappings")


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

    async def delete_after_time(self):
        try:
            result = await self.session.execute(
                delete(UrlMapping).where(
                    func.now()
                    > (UrlMapping.date + (func.interval(UrlMapping.expiration * 3600)))
                )
            )
            await self.session.commit()
            logger.info("All records with expired storage time are deleted")
            return result.rowcount
        except Exception as e:
            logger.error(f"Error when deleting records: {e}")
            await self.session.rollback()
            return 0

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.aclose()
