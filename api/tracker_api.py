import re
from os import getenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, date, time
from typing import Union, Optional
from dotenv import load_dotenv

from api.routers.admin import admin_router
from database.data_base import engine
from helpers.database_helper import DataBaseHelper
from logger.logging_config import logger 
from database import models
from api.auth.jwt_service import JWTService
from api.auth.auth_service import SecurityService
from exceptions.auth_exceptions import GoogleIDMismatchException

app = FastAPI()
security = HTTPBearer()

class News(BaseModel):
    headline: str
    url: str
    news_section: str
    published_at: datetime
    summary: str

class NewsList(BaseModel):
    news: list[News]

class AdminConfig(BaseModel):
    target_email: str
    summary_send_time: time
    last_updated: datetime

ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:4173",  # Vite preview server
]

load_dotenv()
GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
JWT_TOKEN = getenv("JWT_SECRET_KEY")

jwt_service = JWTService(JWT_TOKEN, "HS256")


security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/health-check')
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

@app.get('/keywords', status_code=200)
def get_keywords(): 
    '''
    Gets headlines keywords extracted during the current date.

    :param keyword_number: Specifies the number of keywords to get.
    '''
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    stmt = select(models.ArticleKeywords, models.News).join(models.News.keywords).filter(
        and_(models.ArticleKeywords.extracted_at >= today, models.ArticleKeywords.extracted_at < tomorrow)
    )

    try:
        with Session(engine) as session:
            result = session.execute(stmt).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=501,
            detail="Could not retrieve keywords information."
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error ocurred."
        )

    return [
        {
            "headline": news.headline,
            "keyword_1": keywords.keyword_1,
            "keyword_2": keywords.keyword_2,
            "keyword_3": keywords.keyword_3,
            'extraction_confidence': keywords.extraction_confidence
        }
        for keywords, news in result
    ]


@app.get('/keywords/{id}', status_code=200)
def get_keyword_by_id(id: int):
    '''
    Gets specific keyword set by id

    :param id: Unique id for keywords.
    '''
    stmt = select(models.ArticleKeywords, models.News.headline).join(models.News.keywords).filter(models.ArticleKeywords.id == id)

    try:
        with Session(engine) as session:
            result = session.execute(stmt).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=501,
            detail="Could not retrieve keywords data from data base."
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error ocurred."
        )

    return [
        {
            "headline": headline if headline else "",
            "keyword_1": keywords.keyword_1,
            "keyword_2": keywords.keyword_2,
            "keyword_3": keywords.keyword_3,
            "extracion_confidence": keywords.extraction_confidence
        }
        for keywords, headline in result
    ]
        


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
            models.DailyTrends.start_timestamp >= today,
            models.DailyTrends.start_timestamp < tomorrow 
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
def get_headlines_by_date(date: date):
    '''
    Get headlines for a specific date.

    :param date: Date to retrieve headlines from.
    '''
    next_date = date + timedelta(days=1)

    stmt = select(models.News).where(
        and_(models.News.published_at >= date, models.News.published_at < next_date))
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
        news = [news]
    news_items.extend(news)

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
            "peak_interest": trends.peak_interest,
            "current_interest": trends.current_interest,
            "news_section": news.news_section
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

@app.post("/admin-config", status_code=201)
def post_admin_config(config: AdminConfig):
    '''
    Posts an admin config entry to the database.

    :param config: AdminConfig object containing config data to be inserted.
    '''
    # Validates there's only an @ symbol before the . symbol
    if not re.match(r"[^@]+@[^@]+\.[^@]+", config.target_email):
        logger.error("Wrong format for email.")
        raise HTTPException(
            status_code=400,
            detail="Invalid format for target email."
        )

    session_factory = lambda : Session(engine)

    config_to_insert = models.AdminConfig(
        target_email = config.target_email,
        summary_send_time = config.summary_send_time,
        last_updated = config.last_updated
    )

    try:
        DataBaseHelper.write_orm_objects(config_to_insert, session_factory, logger)
    except SQLAlchemyError:
        logger.error("Failed to write objects to db.")
        raise HTTPException(
            status_code=501,
            detail="Failed to write orm objects to data base."
        )
    except Exception:
        logger.exception("Exception ocurred during data base write.")
        raise HTTPException(
            status_code=500,
            detail="Unexpedted error ocurred."
        )
    
    return config

@app.post("/auth/google/callback")
async def google_auth_callback(request: Request):
    data = await request.json()
    code = data.get("code")
    if not code:
        logger.error("Missing authorization code in request.")
        return JSONResponse(status_code=400, content={"detail": "Missing authorization code."})

    try:
        tokens = SecurityService.exchange_code_for_tokens(
            code,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri="postmessage"
        )
    except HTTPException as e:
        logger.error(f"Failed to exchange code for tokens: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    id_token_str = tokens.get("id_token")
    if not id_token_str:
        logger.error("No ID token returned from Google.")
        return JSONResponse(status_code=400, content={"detail": "No ID token returned from Google."})

    try:
        user_info = SecurityService.verify_id_token(id_token_str, GOOGLE_CLIENT_ID)
    except HTTPException as e:
        logger.error(f"Failed to verify ID token: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    try:
        user = DataBaseHelper.check_or_create_user(user_info, lambda: Session(engine), logger)
    except GoogleIDMismatchException as e:
        logger.error(f"Google ID and email mismatch: {e}")
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except Exception as e:
        logger.error(f"Failed to check or create user: {e}")
        return JSONResponse(status_code=500, content={"detail": "Failed to process user information."})
    app_jwt = jwt_service.create_app_jwt(user)

    return {"token": app_jwt}


app.include_router(admin_router)