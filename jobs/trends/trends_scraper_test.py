import pytest
from unittest import mock
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import os
import json

import sys

# Point Python to your source code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from jobs.trends.trends_scraper import TrendsScraper, run_scraping_job_trends    # Fix 'your_module' to real path

# Typical test values
TRENDING_RESPONSE = {
    'search_parameters' : {
        'geo': 'US',
    },
    'trending_searches': [
        {
            'query': 'AI breakthrough',
            'start_timestamp': 1680655257,
            'search_volume': 100000,
            'increase_percentage': 833,
            'categories': [{'name': 'Technology'}]
        },
        {
            'query': 'New movie',
            'start_timestamp': 1680654257,
            'search_volume': 50000,
            'increase_percentage': 340,
            'categories': [{'name': 'Entertainment'}]
        }
    ]
}


@patch.dict(os.environ, {"TRENDING_NOW_URL": "https://fake.url", "SERP_API_KEY": "fake_key"})
def test_trends_scraper_init_loads_env():
    scraper = TrendsScraper()
    assert scraper._BASE_URL == "https://fake.url"
    assert scraper._API_KEY == "fake_key"
    assert isinstance(scraper._daily_trends, list)


@patch("requests.get")
@patch.dict(os.environ, {"TRENDING_NOW_URL": "https://fake.url", "SERP_API_KEY": "fake_key"})
def test_make_request_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    scraper = TrendsScraper()
    resp = scraper.make_request()
    assert resp.status_code == 200
    mock_get.assert_called_with(url="https://fake.url", params={"api_key": "fake_key"})

@patch("requests.get", side_effect=Exception("Connection error"))
@patch.dict(os.environ, {"TRENDING_NOW_URL": "https://fake.url", "SERP_API_KEY": "fake_key"})
def test_make_request_exception(mock_get):
    scraper = TrendsScraper()
    resp = scraper.make_request()
    assert resp is None


@patch("requests.get")
@patch("database.models.DailyTrends")   # Mock model to prevent real DB/ORM use
@patch.dict(os.environ, {"TRENDING_NOW_URL": "https://fake.url", "SERP_API_KEY": "fake_key"})
def test_poll_daily_trends_populates_and_ranks(mock_dailytrends, mock_requests_get):
    # Prepare mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = json.dumps(TRENDING_RESPONSE)
    mock_requests_get.return_value = mock_resp

    # Configure DailyTrends to create dicts with attributes for test
    def dt_side_effect(**kwargs):
        obj = mock.Mock()
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj
    mock_dailytrends.side_effect = dt_side_effect

    # Run test
    scraper = TrendsScraper()
    scraper.poll_daily_trends()
    trends = scraper.get_daily_trends()
    assert len(trends) == len(TRENDING_RESPONSE['trending_searches'])

    # Check sort
    assert sorted([t.search_volume for t in trends], reverse=True) == [t.search_volume for t in trends]
    # Check assigned ranking
    assert sorted([t.ranking for t in trends]) == [1, 2]


@patch("requests.get")
@patch("database.models.DailyTrends")
@patch.dict(os.environ, {"TRENDING_NOW_URL": "url", "SERP_API_KEY": "key"})
def test_poll_daily_trends_handles_bad_json(mock_dailytrends, mock_requests_get):
    # Response is not JSON
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "BAD JSON"
    mock_requests_get.return_value = mock_resp

    scraper = TrendsScraper()
    # Should not raise; should skip
    scraper.poll_daily_trends()
    assert scraper.get_daily_trends() == []


@patch("requests.get")
@patch.dict(os.environ, {"TRENDING_NOW_URL": "url", "SERP_API_KEY": "key"})
def test_poll_daily_trends_non200(mock_requests_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_requests_get.return_value = mock_resp

    scraper = TrendsScraper()
    scraper.poll_daily_trends()
    assert scraper.get_daily_trends() == []


@patch("database.models.DailyTrends")
def test_rank_daily_trends_sorting(mock_dailytrends):
    scraper = TrendsScraper()
    t1, t2 = mock.Mock(), mock.Mock()
    t1.search_volume, t2.search_volume = 20, 100
    scraper._daily_trends = [t1, t2]
    scraper.rank_daily_trends()
    # Volume should now be descending
    assert scraper._daily_trends[0].search_volume == 100
    assert scraper._daily_trends[0].ranking == 1
    assert scraper._daily_trends[1].ranking == 2

