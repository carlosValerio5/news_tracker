import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
from os import getenv

from database.models import News
from database.data_base import engine
from aws_handler.sqs import AwsHelper
from helpers.database_helper import  DataBaseHelper
from logger.logging_config import logger

class Scraper:
    '''Scraper object to extract bbc news'''

    def __init__(self):
        self._request_URL = "https://bbc.co.uk/news"
        self._navbar_links : list[str] = self._extract_navbar_links()
        self._rss_feeds : list[str] = self._extract_rss_feeds()
        self._news: list[dict] = []
        self._headlines: list[str] = []

    def get_headlines(self) -> list:
        return self._headlines

    def get_rss_feeds(self) -> list:
        return self._rss_feeds

    def get_navbar_links(self) -> list:
        return self._navbar_links

    def get_news(self) -> list:
        return self._news

    def _extract_rss_feeds(self) -> list:

        if len(self._navbar_links) == 0:
            return []


        rss_links = set() 
        for url in self._navbar_links:
            try:
                response = requests.get(url)
            except requests.RequestException as e:
                print(f'Failed to fetch {url}: {e}')
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Exctract rss feeds from link tags
            for link in soup.find_all('link', type='application/rss+xml'):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    rss_links.add(full_url)

            # Extract rss feeds from a tags
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                suffixes = ['rss.xml', 'feed.xml', '.rss', '.xml']
                if any(href.lower().endswith(suffix) for suffix in suffixes):
                    full_url = urljoin(url, href)
                    rss_links.add(full_url)

            time.sleep(1)

        return list(rss_links)

    def _extract_navbar_links(self) -> list:
        try:
            response = requests.get(self._request_URL, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {self._request_URL}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()

        #find main nav elements
        nav_tags = soup.find_all('nav')
        for nav in nav_tags:
            for a in nav.find_all('a', href=True):
                href = a['href']

                #filter hrefs
                if href and not href.startswith('mailto:') and not href.startswith('javascript:'):
                    full_url = urljoin(self._request_URL, href)
                    links.add(full_url)

        return list(links)

    def process_feeds(self) -> list:
        if len(self._rss_feeds) == 0:
            return

        seen = set()
        for feed_url in self._rss_feeds:
            try:
                response = requests.get(feed_url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch {feed_url} : {e}")
                return

            soup = BeautifulSoup(response.text, features="xml")

            items = soup.find_all('item')
            for item in items:
                published_date = item.find('pubDate')
                if published_date:
                    published_date = published_date.get_text().strip()
                    published_date = parse_date(published_date)

                #datetime uses UTC timezone, same timezone as rss feeds
                if published_date < datetime.now() - timedelta(hours=8):
                    continue

                news_section = extract_section_from_url(feed_url)

                headline = item.find('title').get_text()
                url = item.find('link').get_text().strip()

                summary = item.find('description').get_text().strip()

                key = (url, headline)
                if key in seen:
                    continue

                seen.add(key)
                news = {"headline":headline, "url":url, "news_section":news_section, "published_at":published_date, "summary":summary}
                self._headlines.append(headline) 
                self._news.append(news)

                

            time.sleep(1)

            

def parse_date(date_string: str) -> datetime:
    if not date_string or date_string == '':
        return None

    try:
        parsed_date = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    except ValueError as e:
        print("Failed to parse date for {e}")
        return None

    return parsed_date

def extract_section_from_url(url: str) -> str:
    # Parse the URL
    parsed = urlparse(url)
    # Extract the path parts, ignoring empty parts
    parts = [part for part in parsed.path.split('/') if part]

    # If not enough path parts, return None
    if len(parts) < 2 or parts[-1].lower() != "rss.xml":
        return None

    if len(parts) == 2:
        return parts[0]

    elif len(parts) == 3:
        return parts[1]

    elif "topics" in parts:
        try:
            topics_i = parts.index('topics')
            if topics_i + 1 < len(parts):
                return f"topics:{parts[topics_i+1]}"
        except ValueError:
            pass
    return parts[-2]


def run_scraping_job():

    load_dotenv()

    try:
        queue_url = getenv('MAIN_QUEUE_URL')
        fallback_queue_url = getenv('FALLBACK_QUEUE_URL')
    except Exception:
        raise ValueError('Could not load queues URL') 

    #test db connection
    with Session(engine) as session:
        try:
            session.execute(text('Select 1'))
            print('\n\n----------------Connection Successful!')
        except Exception as e:
            print(f'\n\n----------------Connection Failed!:{e}')
            return


    #test sqs connection
    try:
        aws_helper = AwsHelper(queue_url=queue_url, fallback_queue_url=fallback_queue_url)
        print('\n\n----------------SQS Connection Successful!')
    except Exception as e:
        print('\n\n----------------SQS Connection Failed!')
        return

    #extract headlines
    scraper = Scraper()
    scraper.process_feeds()

    session_factory = lambda: Session(engine)

    results = []
    try:
        # If duplicate is found the function will not update.
        results = DataBaseHelper.write_batch_of_objects_returning(News, session_factory, scraper.get_news(), logger, [News.id, News.headline], ['url', 'headline'])
    except Exception:
        logger.error('Failed to write messages to db')

    #send to db
    # with Session(engine) as session:
    #    session.add_all(scraper.get_news())
    #    session.commit()

    if not results:
        logger.error("Failed to write objects to db.")
        return
    #send to sqs queue
    aws_helper.send_batch(results, "headlines", lambda item: json.dumps(item))
    logger.info(f'Headlines count: {len(scraper.get_headlines())}')


if __name__ == '__main__':
    run_scraping_job()