from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


USERNAME = 'your_username'
PASSWORD = 'your_password'
HOST = 'remote_host_address'
PORT = '5432'
DATABASE = 'your_database_name'


DATABASE_URL = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'


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
    

class DataBase(object):    
    def __init__(self):
        engine = create_engine(DATABASE_URL)
		
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
    def __enter__(self):
        return self

    def get_long_url(self, short_value):
        result = (
            self.session
            .query(LongUrl)
            .join(UrlMapping)
            .join(ShortUrl)
            .filter(ShortUrl.short_value == short_value)
            .first()
            )
        return result.long_value if result else None
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
