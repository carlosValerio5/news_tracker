import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

from jobs.bbc.scraper import Scraper, parse_date, extract_section_from_url
from jobs.bbc.scraper import _extract_thumbnail_from_item
from bs4 import BeautifulSoup

# ------------ UNIT TESTS FOR UTILITY FUNCTIONS ------------


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("Tue, 26 Aug 2025 12:38:21 GMT", datetime(2025, 8, 26, 12, 38, 21)),
        ("Wed, 01 Jan 2020 00:00:01 GMT", datetime(2020, 1, 1, 0, 0, 1)),
        ("", None),
        (None, None),
    ],
)
def test_parse_date(date_str, expected):
    result = parse_date(date_str)
    assert (result == expected) or (result is None and expected is None)


@pytest.mark.parametrize(
    "url, expected_section",
    [
        ("https://feeds.bbci.co.uk/news/rss.xml", "news"),
        ("https://feeds.bbci.co.uk/news/technology/rss.xml", "technology"),
        (
            "https://feeds.bbci.co.uk/news/topics/c1vw6q14rzqt/rss.xml",
            "topics:c1vw6q14rzqt",
        ),
        ("https://feeds.bbci.co.uk/sport/football/rss.xml", "football"),
        ("https://feeds.bbci.co.uk/business/rss.xml", "business"),
        ("https://feeds.bbci.co.uk/weird-url-format/notrss.txt", None),
    ],
)
def test_extract_section_from_url(url, expected_section):
    assert extract_section_from_url(url) == expected_section


# ------------ MOCKED TESTS FOR SCRAPER ON MAIN LOGIC ------------


@pytest.fixture
def fake_navbar_html():
    return """
    <html>
      <body>
        <nav>
          <a href="/news">News</a>
          <a href="/news/technology">Tech</a>
          <a href="/sport">Sport</a>
        </nav>
      </body>
    </html>
    """


@pytest.fixture
def fake_section_html():
    return """
    <html>
      <head>
        <link rel="alternate" type="application/rss+xml" href="https://feeds.bbci.co.uk/news/rss.xml"/>
        <link rel="alternate" type="application/rss+xml" href="https://feeds.bbci.co.uk2/news/rss.xml"/>
        <link rel="alternate" type="application/rss+xml" href="https://feeds.bbci.co.uk3/news/rss.xml"/>
      </head>
    </html>
    """


@pytest.fixture
def fake_rss_html():
    pub_date = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %Z")
    return f"""
    <rss>
      <channel>
        <item>
          <title>Headline 1</title>
          <link>https://bbc.co.uk/news/article-1</link>
          <pubDate>{pub_date}</pubDate>
          <description>Summary 1</description>
        </item>
        <item>
          <title>Headline 2</title>
          <link>https://bbc.co.uk/news/article-2</link>
          <pubDate>{pub_date}</pubDate>
          <description>Summary 2</description>
        </item>
      </channel>
    </rss>
    """


@pytest.fixture
def news_class_mock():
    # A stand-in for the News ORM model
    class News:
        def __init__(self, headline, url, news_section, published_at, summary):
            self.headline = headline
            self.url = url
            self.news_section = news_section
            self.published_at = published_at
            self.summary = summary

    return News


@patch("jobs.bbc.scraper.requests.get")
@patch("jobs.bbc.scraper.News")
def test_scraper_process_feeds(
    mock_news,
    mock_requests,
    fake_navbar_html,
    fake_rss_html,
    news_class_mock,
    fake_section_html,
):
    # Mock navbar page
    mock_response_nav = MagicMock()
    mock_response_nav.text = fake_navbar_html
    mock_response_nav.raise_for_status = lambda: None

    mock_response_section = MagicMock()
    mock_response_section.text = fake_section_html
    mock_response_section.raise_for_status = lambda: None

    # Mock RSS feed
    mock_response_rss = MagicMock()
    mock_response_rss.text = fake_rss_html
    mock_response_rss.raise_for_status = lambda: None

    # requests.get must return navbar first, then RSS feed three times
    mock_requests.side_effect = [
        mock_response_nav,
        mock_response_section,
        mock_response_section,
        mock_response_section,
        mock_response_rss,
        mock_response_rss,
        mock_response_rss,
    ]

    # Patch News model for object creation
    mock_news.side_effect = news_class_mock

    # Now, create the scraper - navbar links and feeds will populate based on mocks
    scraper = Scraper()
    assert set(scraper.get_navbar_links()) >= {
        "https://bbc.co.uk/news",
        "https://bbc.co.uk/news/technology",
        "https://bbc.co.uk/sport",
    }

    # temporarily patch sleep to speed up tests
    with patch("jobs.bbc.scraper.time.sleep"):
        scraper.process_feeds()
    news = scraper.get_news()
    assert isinstance(news, list)
    assert len(news) == 2  # Does not store duplicates
    assert all("headline" in n.keys() for n in news)


def test_extract_thumbnail_from_item_media_thumbnail():
    item_xml = '''
    <item>
      <title>With Thumb</title>
      <link>https://bbc.co.uk/news/article-1</link>
      <media:thumbnail width="240" height="134" url="https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/sample.jpg"/>
    </item>
    '''
    item = BeautifulSoup(item_xml, "xml").find("item")
    thumb = _extract_thumbnail_from_item(item)
    assert thumb == "https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/sample.jpg"


def test_extract_thumbnail_from_item_regex_fallback():
    # No thumbnail tag, but raw xml contains url="..." somewhere
    item_xml = '<item><title>X</title><description><img url="https://example.com/img.jpg" /></description></item>'
    item = BeautifulSoup(item_xml, "xml").find("item")
    thumb = _extract_thumbnail_from_item(item)
    assert thumb == "https://example.com/img.jpg"


def test_extract_thumbnail_from_item_malformed_returns_none():
    # Thumbnail tag present but no url attribute -> should return None
    item_xml = '<item><media:thumbnail width="240" height="134" /></item>'
    item = BeautifulSoup(item_xml, "xml").find("item")
    thumb = _extract_thumbnail_from_item(item)
    assert thumb is None


@patch("jobs.bbc.scraper.requests.get")
@patch("jobs.bbc.scraper.News")
def test_scraper_process_feeds_includes_thumbnail(
    mock_news, mock_requests, fake_navbar_html, news_class_mock, fake_section_html
):
    # Similar to test_scraper_process_feeds but include a thumbnail in the RSS
    pub_date = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %Z")
    fake_rss_with_thumb = f"""
    <rss>
      <channel>
        <item>
          <title>Headline Thumb</title>
          <link>https://bbc.co.uk/news/article-1</link>
          <pubDate>{pub_date}</pubDate>
          <description>Summary 1</description>
          <media:thumbnail width="240" height="134" url="https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/thumb.jpg"/>
        </item>
      </channel>
    </rss>
    """

    # Mock navbar and section pages
    mock_response_nav = MagicMock()
    mock_response_nav.text = fake_navbar_html
    mock_response_nav.raise_for_status = lambda: None

    mock_response_section = MagicMock()
    mock_response_section.text = fake_section_html
    mock_response_section.raise_for_status = lambda: None

    mock_response_rss = MagicMock()
    mock_response_rss.text = fake_rss_with_thumb
    mock_response_rss.raise_for_status = lambda: None

    # requests.get order: navbar, section x3, rss x3 (as code expects)
    mock_requests.side_effect = [
        mock_response_nav,
        mock_response_section,
        mock_response_section,
        mock_response_section,
        mock_response_rss,
        mock_response_rss,
        mock_response_rss,
    ]

    mock_news.side_effect = news_class_mock

    scraper = Scraper()
    with patch("jobs.bbc.scraper.time.sleep"):
        scraper.process_feeds()

    news = scraper.get_news()
    assert len(news) >= 1
    # thumbnail is not written to the DB at extraction stage
    assert "thumbnail" not in news[0]

    # the scraper should have recorded the thumbnail separately keyed by URL
    url = news[0]["url"]
    # Try direct key then normalized key
    thumb = None
    if url in scraper._thumbnails:
        thumb = scraper._thumbnails[url]
    else:
        # fallback to any stored key that endswith the basename
        for k, v in scraper._thumbnails.items():
            if k and url and k.endswith(url):
                thumb = v
                break

    assert thumb == "https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/thumb.jpg"

    # simulate the SQS payload builder used later (thumbnail included after DB upload)
    payload = dict(news[0])
    if thumb:
        payload["thumbnail"] = thumb

    assert payload.get("thumbnail") == "https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/thumb.jpg"
