from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, MetaData
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
    keywords_id = Column(Integer, ForeignKey('articlekeywords.id'), nullable=True)

    keywords = relationship('ArticleKeywords', back_populates='news')

class ArticleKeywords(Base):
    '''ArticleKeywords sqlalchemy model'''
    __tablename__ = 'articlekeywords'

    id = Column(Integer, primary_key=True)
    news = relationship('News', back_populates='keywords')
