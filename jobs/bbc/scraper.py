import json
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from os import getenv

from database.models import News
from database.data_base import engine
from aws_handler.sqs import AwsHelper
from helpers.database_helper import DataBaseHelper
from logger.logging_config import logger


class Scraper:
    """Scraper object to extract bbc news"""

    def __init__(self):
        self._request_URL = "https://bbc.co.uk/news"
        self._navbar_links: list[str] = self._extract_navbar_links()
        self._rss_feeds: list[str] = self._extract_rss_feeds()
        self._news: list[dict] = []
        self._headlines: list[str] = []
        # keep thumbnails separate; do not write them to DB at this stage
        self._thumbnails: dict[str, str | None] = {}

    def get_headlines(self) -> list:
        return self._headlines

    def get_rss_feeds(self) -> list:
        return self._rss_feeds

    def get_navbar_links(self) -> list:
        return self._navbar_links

    def get_news(self) -> list:
        return self._news

    def get_thumbnails(self) -> dict:
        return self._thumbnails

    def _extract_rss_feeds(self) -> list:
        if len(self._navbar_links) == 0:
            return []

        rss_links = set()
        for url in self._navbar_links:
            try:
                response = requests.get(url)
            except requests.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            # Exctract rss feeds from link tags
            for link in soup.find_all("link", type="application/rss+xml"):
                href = link.get("href")
                if href:
                    full_url = urljoin(url, href)
                    rss_links.add(full_url)

            # Extract rss feeds from a tags
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                suffixes = ["rss.xml", "feed.xml", ".rss", ".xml"]
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

        soup = BeautifulSoup(response.text, "html.parser")

        links = set()

        # find main nav elements
        nav_tags = soup.find_all("nav")
        for nav in nav_tags:
            for a in nav.find_all("a", href=True):
                href = a["href"]

                # filter hrefs
                if (
                    href
                    and not href.startswith("mailto:")
                    and not href.startswith("javascript:")
                ):
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

            items = soup.find_all("item")
            for item in items:
                published_date = item.find("pubDate")
                if published_date:
                    published_date = published_date.get_text().strip()
                    published_date = parse_date(published_date)

                # datetime uses UTC timezone, same timezone as rss feeds
                if published_date < datetime.now() - timedelta(hours=8):
                    continue

                news_section = extract_section_from_url(feed_url)

                headline = item.find("title").get_text()
                url = item.find("link").get_text().strip()

                summary = item.find("description").get_text().strip()

                # extract thumbnail if present
                thumbnail = _extract_thumbnail_from_item(item)

                key = (url, headline)
                if key in seen:
                    continue

                seen.add(key)
                news = {
                    "headline": headline,
                    "url": url,
                    "news_section": news_section,
                    "published_at": published_date,
                    "summary": summary,
                }
                self._headlines.append(headline)
                # store thumbnail separately (may be None)
                self._thumbnails[url] = thumbnail
                self._news.append(news)

            time.sleep(1)


def parse_date(date_string: str) -> datetime:
    if not date_string or date_string == "":
        return None

    try:
        parsed_date = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError as e:
        logger.error(f"Failed to parse date for {date_string}: {e}")
        return None

    return parsed_date


def extract_section_from_url(url: str) -> str:
    # Parse the URL
    parsed = urlparse(url)
    # Extract the path parts, ignoring empty parts
    parts = [part for part in parsed.path.split("/") if part]

    # If not enough path parts, return None
    if len(parts) < 2 or parts[-1].lower() != "rss.xml":
        return None

    if len(parts) == 2:
        return parts[0]

    elif len(parts) == 3:
        return parts[1]

    elif "topics" in parts:
        try:
            topics_i = parts.index("topics")
            if topics_i + 1 < len(parts):
                return f"topics:{parts[topics_i + 1]}"
        except ValueError:
            pass
    return parts[-2]


def _extract_thumbnail_from_item(item) -> str | None:
    """Extract the thumbnail URL from an RSS <item> element.

    Fast-path: handle tags like
      <media:thumbnail width="240" height="134" url="https://...jpg"/>

    The function checks for namespaced 'thumbnail' tags then looks for
    an attribute named 'url' (or ending with ':url'). Falls back to an
    XML-aware regex that searches for a thumbnail tag with a url attr.
    """

    try:
        # Fast path: find tags named 'media:thumbnail' or any tag ending with ':thumbnail' or 'thumbnail'
        for tag in item.find_all():
            name = getattr(tag, "name", "")
            if not isinstance(name, str):
                continue
            lname = name.lower()
            if "thumbnail" in lname:
                # Prefer explicit 'url' attribute, but accept namespaced attr keys like 'media:url' too
                # Check common attribute keys first
                for key in ("url", "href", "src"):
                    val = tag.get(key)
                    if val and isinstance(val, str) and val.strip():
                        return val.strip()

                # Check any attribute whose local name ends with 'url' (handles namespaced attributes)
                for k, v in tag.attrs.items():
                    if (
                        isinstance(k, str)
                        and k.lower().endswith(":url")
                        or (
                            isinstance(k, str)
                            and k.lower().endswith("url")
                            and k.lower() != "url"
                        )
                    ):
                        if isinstance(v, str) and v.strip():
                            return v.strip()

        # Fallback: first attempt to find a thumbnail tag with a url attribute
        raw = str(item)
        m = re.search(
            r"<[^>]*thumbnail[^>]*\surl\s*=\s*\"([^\"]+)\"", raw, re.IGNORECASE
        )
        if m:
            return m.group(1)

        # If not found, look anywhere in the item for an image URL (jpg/png/etc.)
        img_re = re.compile(
            r"https?://[^\s'\"]+?\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s'\"]*)?",
            re.IGNORECASE,
        )
        m2 = img_re.search(raw)
        if m2:
            return m2.group(0)
    except Exception:
        logger.debug("Failed to extract thumbnail from item", exc_info=True)

    return None


def run_scraping_job():
    load_dotenv()

    try:
        queue_url = getenv("MAIN_QUEUE_URL")
        fallback_queue_url = getenv("FALLBACK_QUEUE_URL")
    except Exception:
        raise ValueError("Could not load queues URL")

    # test db connection
    with Session(engine) as session:
        try:
            session.execute(text("Select 1"))
            logger.info("\n\n----------------Connection Successful!")
        except Exception as e:
            logger.error(f"\n\n----------------Connection Failed!:{e}")
            return

    # test sqs connection
    try:
        aws_helper = AwsHelper(
            queue_url=queue_url, fallback_queue_url=fallback_queue_url
        )
        logger.info("SQS Connection Successful!")
    except Exception as e:
        logger.error("SQS Connection Failed!", extra={"error": e})
        return

    # extract headlines
    scraper = Scraper()
    scraper.process_feeds()

    def session_factory():
        return Session(engine)

    results = []
    news = scraper.get_news()
    # Insert in batches of 25
    for i in range(0, len(news), 25):
        item = news[i : i + 25]
        # If duplicate is found the function will not update.

        try:
            results.extend(DataBaseHelper.write_batch_of_objects_and_return(
                News,
                session_factory,
                item,
                logger,
                [News.id, News.headline, News.url],
                ["url", "headline"],
            ))
        except SQLAlchemyError as e:
            logger.exception("SQLAlchemy error while writing messages to db", extra={"error": e})
        except Exception as e:
            logger.exception("Failed to write messages to db", extra={"error": e})

    if not results:
        logger.error("Failed to write objects to db.")
        return

    # send to sqs queue — include thumbnail in the SQS payload but don't write it to DB
    def sqs_payload(item):
        try:
            url = (
                item.get("url")
                if isinstance(item, dict)
                else getattr(item, "url", None)
            )
            thumbnail = scraper._thumbnails.get(url)
        except Exception:
            thumbnail = None
        # create a shallow copy and add thumbnail if available
        payload = dict(item) if isinstance(item, dict) else item.__dict__
        if thumbnail:
            payload["thumbnail"] = thumbnail
        return json.dumps(payload)

    aws_helper.send_batch(results, "headlines", transform_function=sqs_payload)
    logger.info(f"Thumbnails count: {len(scraper.get_thumbnails())}")
    logger.info(f"Headlines count: {len(scraper.get_headlines())}")


if __name__ == "__main__":
    run_scraping_job()
