from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, MetaData, func
from sqlalchemy.orm import declarative_base, relationship
'''Moduule defining news model'''

meta = MetaData(schema='news_schema')
Base = declarative_base(metadata=meta)

class News(Base):
    '''News model'''

    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    headline = Column(String, nullable=False)
    url = Column(String, nullable=False)
    news_section = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    summary = Column(String)


class DailyTrends(Base):
    '''Daily trends from google trends'''

    __tablename__ = 'dailytrends'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    ranking = Column(Integer)
    geo = Column(String, nullable=False)
    start_timestamp = Column(DateTime, nullable=False)
    search_volume = Column(Integer, nullable = False)
    increase_percentage = Column(Integer, nullable = False)
    category = Column(String)
    scraped_at = Column(DateTime, server_default=func.now())
