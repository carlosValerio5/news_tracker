import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import os

import jobs.trends.trends_scraper as scraper_mod  

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set required environment variables for tests."""
    monkeypatch.setenv("TRENDING_NOW_URL", "http://fakeapi.com/trending")
    monkeypatch.setenv("SERP_API_KEY", "fake_api_key")


def test_fetch_success(monkeypatch):
    """Test TrendsAPI.fetch returns JSON on success."""
    fake_json = {"status": "ok"}
    mock_response = MagicMock()
    mock_response.json.return_value = fake_json
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(scraper_mod.requests, "get", lambda *a, **kw: mock_response)

    api = scraper_mod.TrendsAPI("http://fake", "key")
    result = api.fetch()

    assert result == fake_json


def test_fetch_failure(monkeypatch, caplog):
    """Test TrendsAPI.fetch logs exception and returns None."""
    def fake_get(*args, **kwargs):
        raise scraper_mod.requests.RequestException("Network error")

    monkeypatch.setattr(scraper_mod.requests, "get", fake_get)

    api = scraper_mod.TrendsAPI("http://fake", "key")
    with caplog.at_level(scraper_mod.logging.ERROR):
        result = api.fetch()

    assert result is None
    assert any("Error fetching trends" in rec.message for rec in caplog.records)


def test_parse_payload_builds_rankings():
    """Test parse_payload returns sorted trends with correct ranking."""
    fake_payload = {
        "search_parameters": {"geo": "US"},
        "trending_searches": [
            {
                "query": "Trend A",
                "start_timestamp": datetime(2025, 1, 1).timestamp(),
                "search_volume": 100,
                "increase_percentage": 50,
                "categories": [{"name": "Category A"}],
            },
            {
                "query": "Trend B",
                "start_timestamp": datetime(2025, 1, 2).timestamp(),
                "search_volume": 200,
                "increase_percentage": 70,
                "categories": [{"name": "Category B"}],
            },
        ],
    }

    svc = scraper_mod.TrendsScraperService(api=None, session_factory=None)
    trends = svc.parse_payload(fake_payload)

    # Ranking sorted by search_volume desc
    assert trends[0]["title"] == "Trend B"
    assert trends[0]["ranking"] == 1
    assert trends[1]["ranking"] == 2
    assert trends[1]["title"] == "Trend A"
    assert trends[0]["geo"] == "US"


def test_scrape_and_store_calls_store(monkeypatch):
    """Test scrape_and_store fetches and stores trends."""
    mock_api = MagicMock()
    mock_api.fetch.return_value = {
        "search_parameters": {"geo": "US"},
        "trending_searches": [{
            "query": "Trend X",
            "start_timestamp": datetime(2025, 1, 1).timestamp(),
            "search_volume": 150,
            "increase_percentage": 20,
            "categories": [{"name": "TestCat"}],
        }],
    }

    mock_session = MagicMock()
    session_factory = lambda: mock_session

    svc = scraper_mod.TrendsScraperService(api=mock_api, session_factory=session_factory)

    monkeypatch.setattr(svc, "store_trends", MagicMock())

    num_trends = svc.scrape_and_store()

    assert num_trends == 1
    svc.store_trends.assert_called_once()
    mock_api.fetch.assert_called_once()


def test_store_trends_executes_insert(monkeypatch):
    """Test store_trends executes insert with trends."""
    trends_data = [{
        "title": "Trend Y",
        "start_timestamp": datetime(2025, 1, 1),
        "search_volume": 50,
        "increase_percentage": 10,
        "category": "Cat",
        "geo": "US",
        "ranking": 1
    }]

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    session_factory = lambda: mock_session

    svc = scraper_mod.TrendsScraperService(api=None, session_factory=session_factory)

    # Patch insert to return a mock statement
    mock_stmt = MagicMock()
    monkeypatch.setattr(scraper_mod, "insert", lambda *a, **kw: mock_stmt)
    mock_stmt.values.return_value = mock_stmt
    mock_stmt.on_conflict_do_nothing.return_value = mock_stmt

    svc.store_trends(trends_data)
    mock_session.execute.assert_called_once_with(mock_stmt)
    mock_session.commit.assert_called_once()