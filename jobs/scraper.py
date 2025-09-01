import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
from database.news import News
from sqlalchemy.orm import Session
from database.data_base import engine
class Scraper:
    '''Scraper object to extract bbc news'''

    def __init__(self):
        self.__request_URL = "https://bbc.co.uk/news"
        self.__navbar_links : list[str] = self.__extract_navbar_links()
        self.__rss_feeds : list[str] = self.__extract_rss_feeds()
        self.__news: list[News] = []

    def get_rss_feeds(self) -> list:
        return self.__rss_feeds

    def get_navbar_links(self) -> list:
        return self.__navbar_links

    def get_news(self) -> list:
        return self.__news

    def __extract_rss_feeds(self) -> list:

        if len(self.__navbar_links) == 0:
            return []


        rss_links = set() 
        for url in self.__navbar_links:
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

    def __extract_navbar_links(self) -> list:
        try:
            response = requests.get(self.__request_URL, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {self.__request_URL}")
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
                    full_url = urljoin(self.__request_URL, href)
                    links.add(full_url)

        return list(links)

    def process_feeds(self) -> list:
        if len(self.__rss_feeds) == 0:
            return

        for feed_url in self.__rss_feeds:
            try:
                response = requests.get(feed_url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch {feed_url} : {e}")
                return

            soup = BeautifulSoup(response.text, "xml")

            items = soup.find_all('item')
            for item in items:
                news_section = extract_section_from_url(feed_url)

                headline = item.find('title').get_text()
                url = item.find('link').get_text().strip()

                published_date = item.find('pubDate').get_text().strip()
                published_date = parse_date(published_date)

                summary = item.find('description').get_text().strip()

                news = News(headline=headline, url=url, news_section=news_section, published_at=published_date, summary=summary)
                self.__news.append(news)

                

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

    # We expect 'rss.xml' as the last part
    if parts and parts[-1].lower() == 'rss.xml':
        # section is the part before 'rss.xml'
        if len(parts) >= 2:
            return parts[-2]
    return None

scraper = Scraper()
scraper.process_feeds()

with Session(engine) as session:
    session.add_all(scraper.get_news())
    session.commit()