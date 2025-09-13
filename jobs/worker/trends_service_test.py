import pytest
from unittest.mock import patch
from datetime import date, timedelta
from requests import HTTPError

from jobs.worker.worker import GoogleTrendsService  


@pytest.fixture
def service():
    return GoogleTrendsService(base_url="http://fake", api_key="test-key")


# -------------------------------
# estimate_popularity
# -------------------------------

def test_estimate_popularity_success(service):
    payload = {
        "interest_over_time": {
            "timeline_data": [
                {"date": "Feb 1 – Feb 7, 2025", "values": {"extracted_value": 80}},
                {"date": "Feb 8 – Feb 14, 2025", "values": {"extracted_value": 100}},
            ]
        }
    }

    with patch.object(service, 'get_api_payload', return_value=payload), \
         patch.object(service, 'get_current_interest', return_value=50), \
         patch.object(service, 'get_peak_interest', return_value=100), \
         patch.object(service, 'get_start_end_date', return_value=(date(2025, 2, 1), date(2025, 2, 14))):

        results = service.estimate_popularity("Apple")
        assert results["current_interest"] == 50
        assert results["peak_interest"] == 100
        assert results["data_period_start"] == date(2025, 2, 1)
        assert results["data_period_end"] == date(2025, 2, 14)
        assert results["has_data"] is True


def test_estimate_popularity_http_error_logs_and_returns_none(service, caplog):
    with patch.object(service, 'get_api_payload', side_effect=HTTPError()):
        with caplog.at_level("ERROR"):
            result = service.estimate_popularity("Apple")
    assert result is None
    assert "Failed to make request" in caplog.text


def test_estimate_popularity_unexpected_exception_logs(service, caplog):
    with patch.object(service, 'get_api_payload', side_effect=Exception("unexpected")):
        with caplog.at_level("ERROR"):
            result = service.estimate_popularity("Apple")
    assert result is None
    assert "Unexpected error ocurred" in caplog.text


def test_estimate_popularity_keyerror_logs_and_returns_none(service, caplog):
    payload = {}
    with patch.object(service, 'get_api_payload', return_value=payload), \
         patch.object(service, 'get_current_interest', return_value=50), \
         patch.object(service, 'get_peak_interest', return_value=100), \
         patch.object(service, 'get_start_end_date', side_effect=KeyError("fail")):
        with caplog.at_level("ERROR"):
            result = service.estimate_popularity("Apple")
    assert result is None
    assert "Failed to get date period data" in caplog.text


def test_estimate_popularity_sets_has_data_false_when_both_minus_one(service):
    payload = {}
    with patch.object(service, 'get_api_payload', return_value=payload), \
         patch.object(service, 'get_current_interest', return_value=-1), \
         patch.object(service, 'get_peak_interest', return_value=-1), \
         patch.object(service, 'get_start_end_date', return_value=(date(2025, 1, 1), date(2025, 1, 7))):

        results = service.estimate_popularity("Apple")
        assert results['has_data'] is False


# -------------------------------
# get_peak_interest
# -------------------------------

def test_get_peak_interest_success(service):
    payload = {
        "interest_over_time": {
            "timeline_data": [
                {"values": [{"extracted_value": 50}]},
                {"values": [{"extracted_value": 100}]},
            ]
        }
    }
    assert service.get_peak_interest(payload) == 100


def test_get_peak_interest_missing_interest_over_time_logs_and_minus1(service, caplog):
    payload = {}
    with caplog.at_level("WARNING"):
        result = service.get_peak_interest(payload)
    assert result == -1
    assert "Could not extract interest over time data" in caplog.text


def test_get_peak_interest_no_timeline_data_logs(service, caplog):
    payload = {"interest_over_time": {
        'dummy': {}
    }}
    with caplog.at_level("WARNING"):
        result = service.get_peak_interest(payload)
    assert result == -1
    assert "Could not extract timeline data" in caplog.text


def test_get_peak_interest_entry_missing_values_logs(service, caplog):
    payload = {
        "interest_over_time": {
            "timeline_data": [
                {"date": "Feb 1 – Feb 7, 2025"}
            ]
        }
    }
    with caplog.at_level("WARNING"):
        result = service.get_peak_interest(payload)
    assert result == -1
    assert "No data for date" in caplog.text


# -------------------------------
# get_current_interest
# -------------------------------

def test_get_current_interest_success(service):
    # Pick a date range that includes today
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    date_str = f"{yesterday.strftime('%b %d')} – {today.strftime('%b %d')}, {today.year}"
    payload = {
        "search_parameters" : {"q" : "test"},
        "interest_over_time": {
            "timeline_data": [
                {"date": date_str, "values": [{"query": "test", "extracted_value": 55}]}
            ]
        }
    }
    with patch.object(service, 'get_date_interval', return_value=(today.replace(day=1), today.replace(day=28))):
        assert service.get_current_interest(payload) == 55


def test_get_current_interest_missing_interest_over_time(service, caplog):
    payload = {}
    with caplog.at_level("WARNING"):
        assert service.get_current_interest(payload) == -1
    assert "Could not extract interest over time data" in caplog.text


def test_get_current_interest_no_timeline_data(service, caplog):
    payload = {"interest_over_time": {
        'dummy' : {}
    }}
    with caplog.at_level("WARNING"):
        assert service.get_current_interest(payload) == -1
    assert "Could not extract timeline data" in caplog.text


def test_get_current_interest_no_date_match(service, caplog):
    payload = {
        "search_parameters": {"q": "Test"},
        "interest_over_time": {
            "timeline_data": [
                {"date": "Feb 1 – Feb 7, 2025", "values": [{"extracted_value": 44}]}
            ]
        }
    }
    with patch.object(service, 'get_date_interval', return_value=(date(2000, 1, 1), date(2000, 1, 2))):
        with caplog.at_level("ERROR"):
            assert service.get_current_interest(payload) == -1
    assert "Could not find current date" in caplog.text


def test_get_current_interest_entry_missing_values(service, caplog):
    today = date.today()
    payload = {
        "search_parameters": {"q": "Test"},
        "interest_over_time": {
            "timeline_data": [
                {"date": "dummy", "values": None}
            ]
        }
    }
    with patch.object(service, 'get_date_interval', return_value=(today.replace(day=1), today.replace(day=28))):
        with caplog.at_level("ERROR"):
            assert service.get_current_interest(payload) == -1
    assert "Could not extract information for keyword" in caplog.text


# -------------------------------
# get_date_interval
# -------------------------------

def test_get_date_interval_parses_correctly(service):
    start, end = service.get_date_interval("Feb 1 – Feb 7, 2025")
    assert isinstance(start, date)
    assert isinstance(end, date)


# -------------------------------
# get_start_end_date
# -------------------------------

def test_get_start_end_date_success(service):
    payload = {
        "interest_over_time": {
            "timeline_data": [
                {"date": "Feb 1 – Feb 7, 2025"},
                {"date": "Feb 8 – Feb 14, 2025"}
            ]
        }
    }
    with patch.object(service, 'get_date_interval', side_effect=[
        (date(2025, 2, 1), date(2025, 2, 7)),
        (date(2025, 2, 8), date(2025, 2, 14))
    ]):
        start, end = service.get_start_end_date(payload)
        assert start == date(2025, 2, 1)
        assert end == date(2025, 2, 14)


def test_get_start_end_date_missing_interest_over_time(service):
    with pytest.raises(KeyError):
        service.get_start_end_date({})

def test_get_start_end_date_missing_timeline_data(service):
    with pytest.raises(KeyError):
        service.get_start_end_date({"interest_over_time": {}})