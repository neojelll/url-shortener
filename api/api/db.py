<<<<<<< Updated upstream
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import select
from datetime import datetime, time, timedelta
=======
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs, async_sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import select
>>>>>>> Stashed changes
from loguru import logger

USERNAME = "your_username"
PASSWORD = "your_password"
HOST = "remote_host_address"
PORT = "5432"
DATABASE = "your_database_name"

<<<<<<< Updated upstream
DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

=======
>>>>>>> Stashed changes
class Base(AsyncAttrs, DeclarativeBase):
    pass

class LongUrl(Base):
<<<<<<< Updated upstream
    __tablename__ = 'long_url'
=======
    __tablename__ = "long_url"
>>>>>>> Stashed changes
    long_id = Column(Integer, primary_key=True)
    long_value = Column(String(250), unique=True, nullable=False)

class ShortUrl(Base):
<<<<<<< Updated upstream
    __tablename__ = 'short_url'
=======
    __tablename__ = "short_url"
>>>>>>> Stashed changes
    short_id = Column(Integer, primary_key=True)
    short_value = Column(String(250), nullable=False)

class UrlMapping(Base):
<<<<<<< Updated upstream
    __tablename__ = 'url_mapping'
    short_id = Column(Integer, ForeignKey('short_url.short_id'), primary_key=True)
    long_id = Column(Integer, ForeignKey('long_url.long_id'), nullable=False)
    expiration = Column(Integer, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
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
=======
    __tablename__ = "url_mapping"
    short_id = Column(String(20), ForeignKey("short_url.short_id"), primary_key=True)
    long_id = Column(Integer, ForeignKey("long_url.long_id"), nullable=False)
    expiration = Column(Integer, nullable=False)
    short_url = relationship("ShortUrl", backref="url_mappings")
    long_url = relationship("LongUrl", backref="url_mappings")

class DataBase():
    async def __init__(self):
        self.async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
        self.async_sessionmaker = async_sessionmaker(bind=self.async_engine, class_=AsyncSession, expire_on_commit=False)

    async def __aenter__(self):
        self.async_session = await self.async_sessionmaker() #type: ignore
        return self
    
    async def get_long_url(self, short_value):
        try:
            result = await self.async_session.execute(
>>>>>>> Stashed changes
                select(LongUrl)
                .join(UrlMapping)
                .join(ShortUrl)
                .where(ShortUrl.short_value == short_value)
<<<<<<< Updated upstream
            )          
            long_url = result.scalars().first()
            if long_url is not None:
                return long_url.long_value
            return None
        except Exception as e:
            logger.error(f"An error occurred while fetching long URL: {e}")
            return None
        
    async def get_expiration(self, short_value):
        try:
            result = await self.session.execute(
                select(UrlMapping)
                .join(ShortUrl)
                .where(ShortUrl.short_value == short_value)
            )
            url_mapping = result.scalars().first()
            if url_mapping is not None:
                expiration, date = url_mapping.expiration, url_mapping.date
                create_time = date.hour
                current_time = datetime.now().time().hour
                return max(int((create_time + expiration) - current_time), 0)
            return None
=======
            )

            long_url = result.scalars().first()

            if long_url is not None:
                return long_url.long_value
            return None

>>>>>>> Stashed changes
        except Exception as e:
            logger.error(f"An error occurred while fetching long URL: {e}")
            return None

    async def __aexit__(self, exc_type, exc_value, traceback):
<<<<<<< Updated upstream
        await self.session.aclose()
      
=======
        await self.async_session.aclose()
>>>>>>> Stashed changes
