from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import Union, Optional

from database.data_base import engine
from helpers.database_helper import DataBaseHelper
from logger.logging_config import logger 
from database import models

app = FastAPI()

class News(BaseModel):
    headline: str
    url: str
    news_section: str
    published_at: str
    summary: str

class NewsList(BaseModel):
    news: list[News]


@app.get('/')
def health_check():
    '''Checks health api, sqs and db connections.'''
    try:
        DataBaseHelper.check_database_connection(lambda: Session(engine), logger)
    except (SQLAlchemyError):
        return {'Status': 'Unavailable'}
    return {'Status': 'Available'}

@app.get('/headlines', status_code=200)
def get_headlines():
    '''Gets todays news headlines.'''
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today = today.date()
    tomorrow = tomorrow.date()
    stmt = select(models.News).where(and_(
        models.News.published_at < tomorrow,
        models.News.published_at >= today
        )).order_by(desc(models.News.published_at))
    try:
        with Session(engine) as session:
            result = session.execute(stmt).scalars().all()
    except SQLAlchemyError:
        logger.exception(f'Failed to retrieve news for date {today}')
        raise HTTPException(
            status_code=501,
            detail='Failed to retrieve data for headlines.'
        )
    response = [
        {
            'headline': news.headline,
            'published_at': news.published_at,
            'section': news.news_section
        }
        for news in result
    ]
    return response

@app.get('/keywords')
def get_keywords(): # use nlp service or get from db, if from db keywords max = 3
    '''
    Gets headlines keywords

    :param keyword_number: Specifies the number of keywords to get.
    '''


@app.get('/keywords/{id}')
def get_keyword_by_id(keywords_id: int):
    '''
    Gets specific keyword set by id

    :param keywords_id: Unique id for keywords.
    '''
    pass

@app.get('/trending-now')
def get_trending_now_trends():
    '''
    Gets today's most popular trends.
    '''
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today = today.date()
    tomorrow = tomorrow.date()


    stmt = select(models.DailyTrends).limit(50).where(
        and_(
            models.DailyTrends.start_timestamp >= "2025-09-04",
            models.DailyTrends.start_timestamp < "2025-09-05"
            )
    ).order_by(models.DailyTrends.ranking)
    results = None
    try:
        with Session(engine) as session:
            results = session.execute(stmt).scalars().all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=501,
            detail='Failed to retrieve current trends.'
        )
    
    todays_trends = [
        {
            "title":trends.title,
            "ranking":trends.ranking,
            "increase_percentage": trends.increase_percentage,
            "search_volume":trends.search_volume,
            "scraped_at":trends.scraped_at
        }
        for trends in results
    ]
    return todays_trends



@app.get('/headlines/{date}', status_code=200)
def get_headlines_by_date(date: str):
    '''
    Get headlines for a specific date.

    :param date: Date to retrieve headlines from.
    '''
    try:
        date_filter = datetime.strptime(date, '%Y-%m-%d')
        date_tomorrow = date_filter + timedelta(days=1)
        date_filter = date_filter.date()
        date_tomorrow = date_tomorrow.date()
    except Exception:
        raise HTTPException(
            status_code=501,
            detail=f'Failed to parse date: {date}'
        )

    stmt = select(models.News).where(
        and_(models.News.published_at >= date_filter, models.News.published_at < date_tomorrow))
    result = []
    try:
        with Session(engine) as session:
            result = session.execute(stmt).scalars().all()
    except Exception:
        raise HTTPException(
            status_code=501,
            detail=f'Failed to retrieve headlines for date {date}'
        )

    response = [
        {
        "id": news.id,
        "headline": news.headline,
        "url": news.url,
        "published_at": news.published_at
        }
        for news in result
    ]
    return response 

@app.post('/headlines', status_code=201)
def post_headline(news: Union[News, NewsList]):
    '''
    Posts a headline to the data base.
    '''
    news_items = []
    if isinstance(news, News):
        news_items.append(news)

    if isinstance(news, NewsList):
        news_items = news.news

    session_factory = lambda: Session(engine)
    items_to_write = []
    for item in news_items:
        news_to_insert = models.News(
        headline = item.headline,
        url = item.url,
        news_section = item.news_section,
        published_at = item.published_at,
        summary = item.summary  
        )
        items_to_write.append(news_to_insert)

    try:
        DataBaseHelper.write_orm_objects(items_to_write, session_factory, logger)
    except SQLAlchemyError:
        logger.exception('Failed to write object to db.')
        raise HTTPException(
            status_code=501,
            detail='Failed to write headlines to data base.'
        )
    except Exception:
        raise HTTPException(
            status_code=500
            ,detail= 'Unexpected error ocurred.'
        )

    return news

@app.get("/news-report", status_code=200)
def get_news_report():
    '''
    Gets the current news report.
    '''
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today = today.date()
    tomorrow = tomorrow.date()

    stmt = select(models.News, models.TrendsResults).join(models.News.keywords).join(models.ArticleKeywords.trends_result).where(
        and_(models.News.published_at >= today, models.News.published_at < tomorrow)
    )

    try:
        with Session(engine) as session:
            results = session.execute(stmt).all()
    except SQLAlchemyError:
        logger.exception("Internal ORM error.")
        raise HTTPException(
            status_code=501
            ,detail="Failed to retrieve report information."
        )
    
    news_report = [
        {
            "headline":news.headline,
            "summary": news.summary,
            "url": news.url,
            "peak_intereset": trends.peak_interest,
            "current_interest": trends.current_interest,
        }
        for news, trends, in results if trends.has_data 
    ]

    return news_report


@app.get("/admin-config")
def get_admin_config(id: Optional[int]=None, email: Optional[str]=None):
    '''
    Gets the admin config for a specific id.

    :param id: Id of admin config.
    '''
    if id:
        stmt = select(models.AdminConfig).filter(models.AdminConfig.id == id)

    elif email:
        stmt = select(models.AdminConfig).filter(models.AdminConfig.target_email == email)

    try:
        with Session(engine) as session:
            results = session.execute(stmt).scalars().all()
    except SQLAlchemyError:
        logger.error('Failed to retrieve admin config data.')
        raise

    return [
        {
            "id": config.id,
            "target_email": config.target_email,
            "summary_send_time": config.summary_send_time,
            "last_updated": config.last_updated,
        }
        for config in results
    ]
