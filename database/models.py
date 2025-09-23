from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, MetaData, func, Numeric, Boolean, Date, Computed, Index
from sqlalchemy.orm import declarative_base, relationship, mapped_column, Mapped 
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

    keywords_id: Mapped[int] = mapped_column(ForeignKey('articlekeywords.id'))
    keywords: Mapped['ArticleKeywords'] = relationship(back_populates='news_article')

    Index(
        'uq_news_url_headline'
        ,'url'
        , 'headline'
        ,unique = True
    )


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

class ArticleKeywords(Base):
    '''Processed headlines separated into keywords'''

    __tablename__ = 'articlekeywords'
    id = Column(Integer, primary_key=True)
    keyword_1 = Column(String, nullable=False)
    keyword_2 = Column(String)
    keyword_3 = Column(String)
    extraction_confidence = Column(Numeric(3, 2))
    extracted_at = Column(DateTime, server_default=func.now())
    composed_query = Column(String, Computed(
        "lower(coalesce(keyword_1, '')) || '|' || lower(coalesce(keyword_2, '')) || '|' || lower(coalesce(keyword_3, ''))", persisted=True
        ))

    Index (
        'uq_composed_query',
        'composed_query',
        unique=True
    )

    news_article: Mapped['News'] = relationship(back_populates='keywords')
    trends_result: Mapped['TrendsResults'] = relationship(back_populates='article_keyword')

class TrendsResults(Base):
    '''Popularity results for extracted keywords'''

    __tablename__ = 'trendsresults'
    id = Column(Integer, primary_key=True)
    has_data = Column(Boolean, nullable=False)
    peak_interest = Column(Integer)
    avg_interest = Column(Numeric(5,2))
    current_interest = Column(Integer, nullable=False)
    data_collected_at = Column(DateTime, nullable=False, server_default=func.now())
    data_period_start = Column(Date)
    data_period_end = Column(Date)
    updated_at = Column(DateTime, server_default=func.now())
    geo = Column(String)

    article_keywords_id: Mapped[int] = mapped_column(ForeignKey('articlekeywords.id')) 
    article_keyword: Mapped['ArticleKeywords'] = relationship(back_populates="trends_result")