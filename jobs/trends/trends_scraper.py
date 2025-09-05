import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.models import DailyTrends
from database.data_base import engine

'''Business logic for Google daily trends scraping'''
class TrendsScraper:
    '''Handling Daily trends logic'''

    def __init__(self):
        load_dotenv()
        self._BASE_URL = os.getenv('TRENDING_NOW_URL')
        self._API_KEY = os.getenv('SERP_API_KEY')
        self._daily_trends: list[DailyTrends] = []

    '''Daily Trend list getter'''
    def get_daily_trends(self):
        return self._daily_trends


    '''Make a single request for daily trends'''
    def make_request(self):
        params = {
            'api_key' : self._API_KEY
        }

        try:
            response = requests.get(url=self._BASE_URL, params=params)
        except Exception as e:
            print(f'Failed to fetch request: {e}')
            return None
        
        return response

    '''Polls for daily trends and ranks trends'''
    def poll_daily_trends(self):

        #Avoid polling multiple times to reduce API calls
        if len(self._daily_trends) > 0:
            return

        result= self.make_request()

        if result == None:
            return
        
        if result.status_code != 200:
            print(f'Request failed: {result.status_code}')
            return

        try:
            payload = json.loads(result.text) 
        except json.JSONDecodeError as e:
            print(f'Failed to load json: {e}')
            return

        geo = payload['search_parameters']['geo']
        
        self._daily_trends = []

        for trend in payload['trending_searches']:
            title = trend['query']

            try:
                start_timestamp = datetime.fromtimestamp(trend['start_timestamp'])
            except Exception as e:
                print(f'Unable to get start time for trend {title}')
                continue

            search_volume = trend['search_volume']
            increase_percentage = trend['increase_percentage']

            #categories is a json object containing several categories
            category = trend['categories'][0]['name']

            try:
                trend_object = DailyTrends(title=title, start_timestamp=start_timestamp, search_volume=search_volume, 
                                        increase_percentage=increase_percentage, category=category, geo=geo)
            except Exception as e:
                print(f"Unable to load object: {e}")
                continue

            self._daily_trends.append(trend_object)

        self.rank_daily_trends()
        

    '''Ranks trends by search volume'''
    def rank_daily_trends(self):
        self._daily_trends.sort(key=lambda x: x.search_volume, reverse=True)

        for rank, trend in enumerate(self._daily_trends):
            trend.ranking = rank + 1

    '''Stores trends to DB'''
    def store_daily_trends(self):
        try:
            with Session(engine) as session:
                session.add_all(self._daily_trends)
                session.commit()
        except Exception as e:
            raise Exception(e)


def run_scraping_job_trends():
    scraper = TrendsScraper()

    with Session(engine) as session:
        try:
            session.execute(text('SELECT 1'))
            print(f"Connection to DB successful!")
        except Exception as e:
            print(f"Failed to make connection with DB: {e}")
            raise Exception(e)
    
    scraper.poll_daily_trends()
    
    try:
        scraper.store_daily_trends()
    except Exception as e:
        print(f'Unable to make transaction to DB: {e}')
        raise Exception(e)

    print(f'Trends Fetched: {len(scraper.get_daily_trends())}')


if __name__ == '__main__':
    run_scraping_job_trends()