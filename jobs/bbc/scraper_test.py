import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

from jobs.bbc.scraper import (
    Scraper,
    parse_date,
    extract_section_from_url
)

# ------------ UNIT TESTS FOR UTILITY FUNCTIONS ------------

@pytest.mark.parametrize("date_str, expected", [
    ("Tue, 26 Aug 2025 12:38:21 GMT", datetime(2025, 8, 26, 12, 38, 21)),
    ("Wed, 01 Jan 2020 00:00:01 GMT", datetime(2020, 1, 1, 0, 0, 1)),
    ("", None),
    (None, None)
])
def test_parse_date(date_str, expected):
    result = parse_date(date_str)
    assert (result == expected) or (result is None and expected is None)

@pytest.mark.parametrize("url, expected_section", [
    ("https://feeds.bbci.co.uk/news/rss.xml", "news"),
    ("https://feeds.bbci.co.uk/news/technology/rss.xml", "technology"),
    ("https://feeds.bbci.co.uk/news/topics/c1vw6q14rzqt/rss.xml", "topics:c1vw6q14rzqt"),
    ("https://feeds.bbci.co.uk/sport/football/rss.xml", "football"),
    ("https://feeds.bbci.co.uk/business/rss.xml", "business"),
    ("https://feeds.bbci.co.uk/weird-url-format/notrss.txt", None),
])
def test_extract_section_from_url(url, expected_section):
    assert extract_section_from_url(url) == expected_section

# ------------ MOCKED TESTS FOR SCRAPER ON MAIN LOGIC ------------

@pytest.fixture
def fake_navbar_html():
    return '''
    <html>
      <body>
        <nav>
          <a href="/news">News</a>
          <a href="/news/technology">Tech</a>
          <a href="/sport">Sport</a>
        </nav>
      </body>
    </html>
    '''

@pytest.fixture
def fake_section_html():
    return '''
    <html>
      <head>
        <link rel="alternate" type="application/rss+xml" href="https://feeds.bbci.co.uk/news/rss.xml"/>
        <link rel="alternate" type="application/rss+xml" href="https://feeds.bbci.co.uk2/news/rss.xml"/>
        <link rel="alternate" type="application/rss+xml" href="https://feeds.bbci.co.uk3/news/rss.xml"/>
      </head>
    </html>
    '''

@pytest.fixture
def fake_rss_html():
    pub_date = datetime.now(UTC).strftime('%a, %d %b %Y %H:%M:%S %Z')
    return f'''
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
    '''

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

@patch('jobs.bbc.scraper.requests.get')
@patch('jobs.bbc.scraper.News')
def test_scraper_process_feeds(mock_news, mock_requests, fake_navbar_html, fake_rss_html, news_class_mock, fake_section_html):
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
        mock_response_rss
        ]

    # Patch News model for object creation
    mock_news.side_effect = news_class_mock

    # Now, create the scraper - navbar links and feeds will populate based on mocks
    scraper = Scraper()
    assert set(scraper.get_navbar_links()) >= {
        "https://bbc.co.uk/news",
        "https://bbc.co.uk/news/technology",
        "https://bbc.co.uk/sport"
    }

    # temporarily patch sleep to speed up tests
    with patch('jobs.bbc.scraper.time.sleep'):
        scraper.process_feeds()
    news = scraper.get_news()
    assert isinstance(news, list)
    assert len(news) == 6  # 2 items per RSS feed, 3 links
    assert all(hasattr(n, 'headline') for n in news)

# Additional tests (such as error handling, edge cases, etc.) are possible.
# For real scenarios, also mock soup parsing if you want to isolate even further.
