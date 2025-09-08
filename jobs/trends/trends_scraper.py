import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from database.models import DailyTrends
from database.data_base import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendsAPI:
    '''API handler for Google Trends'''
    def __init__(self, base_url, api_key):
        self._url = base_url
        self._key = api_key
    
    def fetch(self):
        try:
            r = requests.get(self._url, params={'api_key': self._key}, timeout=(3, 10))
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            logger.exception("Error fetching trends")
            return None

'''Business logic for Google daily trends scraping'''
class TrendsScraperService:
    '''Handling Daily trends logic'''

    def __init__(self, api, session_factory):
        self.api = api
        self.session_factory = session_factory

    '''Scrapes daily trends and store thems in Data Base'''
    def scrape_and_store(self):
        payload = self.api.fetch()
        if not payload:
            return 0
        
        trends = self.parse_payload(payload)
        self.store_trends(trends)
        return len(trends)


    '''Parses json object result from fetching'''
    def parse_payload(self, payload):
        geo = payload.get('search_parameters', {}).get('geo', 'UNKNOWN')
        trends = []
        for t in payload.get('trending_searches', []):
            try:
                trends.append({
                    'title': t.get('query'),
                    'start_timestamp': datetime.fromtimestamp(t.get('start_timestamp', 0)),
                    'search_volume': t.get('search_volume'),
                    'increase_percentage': t.get('increase_percentage'),
                    'category': t.get('categories', [{}])[0].get('name', ''),
                    'geo': geo
                })
            except Exception:
                logger.warning("Skipping malformed trend %s", t)
            
        trends.sort(key=lambda x: x['search_volume'] or 0, reverse=True)
        for rank, trend in enumerate(trends, start=1):
            trend['ranking'] = rank

        return trends
    
    '''Stores trends in data base'''
    def store_trends(self, trends):
        with self.session_factory() as session:
            stmt = insert(DailyTrends).values(trends).on_conflict_do_nothing()
            session.execute(stmt)
            session.commit()



def run_scraping_job_trends():
    load_dotenv()
    url = os.getenv("TRENDING_NOW_URL")
    if not url:
        raise ValueError("TRENDING_NOW_URL not set")
    
    key = os.getenv("SERP_API_KEY")
    if not key:
        raise ValueError("SERP_API_KEY not set")


    api = TrendsAPI(url, key)
    session_factory = lambda: Session(engine)
    
    with session_factory() as session:
        try:
            session.execute(text("SELECT 1"))
        except Exception:
            logger.exception("Error making connection to Data Base")


    scraper = TrendsScraperService(api, session_factory)

    number_of_trends = scraper.scrape_and_store()
    logger.info("Number of trends stored: %d", number_of_trends)


if __name__ == '__main__':
    run_scraping_job_trends()