from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import select
from loguru import logger


USERNAME = 'your_username'
PASSWORD = 'your_password'
HOST = 'remote_host_address'
PORT = '5432'
DATABASE = 'your_database_name'


DATABASE_URL = f'postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

Base = declarative_base()

class LongUrl(Base):
    __tablename__ = 'long_url'

    long_id = Column(Integer, primary_key=True)
    long_value = Column(Text, unique=True, nullable=False)


class ShortUrl(Base):
    __tablename__ = 'short_url'

    short_id = Column(String(20), primary_key=True)
    short_value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)


class UrlMapping(Base):
    __tablename__ = 'url_mapping'

    short_id = Column(String(20), ForeignKey('short_url.short_id'), primary_key=True)
    long_id = Column(Integer, ForeignKey('long_url.long_id'), nullable=False)
    expiration_date = Column(TIMESTAMP)

    short_url = relationship('ShortUrl', backref='url_mappings')
    long_url = relationship('LongUrl', backref='url_mappings')


class DataBase:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, echo=True, future=True)
        self.async_sessionmaker = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        
    async def __aenter__(self):
        self.session = await self.async_sessionmaker() #type: ignore
        return self

    async def get_long_url(self, short_value):
        try:
            result = await self.session.execute(
                select(LongUrl)
                .join(UrlMapping)
                .join(ShortUrl)
                .where(ShortUrl.short_value == short_value)
            )

            long_url = result.scalars().first()

            if long_url is not None:
                return long_url.long_value
            return None

        except Exception as e:
            logger.error(f"An error occurred while fetching long URL: {e}")
            return None

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()
      