from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = ""

Base = declarative_base()

class ShortUrl(Base):
    __tablename__ = "short_url"
	
    short_id = Column(Integer, primary_key=True)
    short_value = Column(String(250), unique=True, nullable=False)

class LongUrl(Base):
    __tablename__ = "long_url"

    long_id = Column(Integer, primary_key=True)
    long_value = Column(String(250), nullable=False)

class UrlMapping(Base):
    __tablename__ = "url_mapping"

    short_id = Column(Integer, ForeignKey("short_url.short_id"), primary_key=True)
    long_id = Column(Integer, ForeignKey("long_url.long_id"), nullable=False)
    expiration = Column(Integer, nullable=False)

    short_url = relationship("ShortUrl", backref="url_mappings")
    long_url = relationship("LongUrl", backref="url_mappings")

class DataBase():
    def __init__(self):
        self.async_engine = create_async_engine(DATABASE_URL)
        self.async_connect = self.async_engine.connect()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.async_connect.aclose()