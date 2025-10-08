from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from helpers.database_helper import DataBaseHelper
from api.tracker_api import app
from unittest.mock import MagicMock

client = TestClient(app)


# Utility: create a mocked Session context manager
def make_mock_session(
    execute_result=None, scalars_result=None, execute_side_effect=None
):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    if execute_side_effect:
        mock_session.execute.side_effect = execute_side_effect
    else:
        exec_mock = MagicMock()
        if scalars_result is not None:
            exec_mock.scalars.return_value.all.return_value = scalars_result
        if execute_result is not None:
            exec_mock.all.return_value = execute_result
        mock_session.execute.return_value = exec_mock

    return mock_session


# -------------------------
# health_check test
# -------------------------


def test_health_check_available(mocker):
    mocker.patch.object(DataBaseHelper, "check_database_connection", return_value=None)
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"Status": "Available"}


def test_health_check_unavailable(mocker):
    mocker.patch.object(
        DataBaseHelper, "check_database_connection", side_effect=SQLAlchemyError()
    )
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"Status": "Unavailable"}


# -----------------------
# get_headlines test
# -----------------------


def test_get_headlines_success(mocker):
    mock_news = [
        type(
            "News",
            (),
            {
                "headline": "Title1",
                "published_at": "2025-09-17",
                "news_section": "Tech",
            },
        )(),
        type(
            "News",
            (),
            {
                "headline": "Title2",
                "published_at": "2025-09-17",
                "news_section": "Business",
            },
        )(),
    ]

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = mock_news
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/headlines")
    assert response.status_code == 200
    assert response.json() == [
        {"headline": "Title1", "published_at": "2025-09-17", "section": "Tech"},
        {"headline": "Title2", "published_at": "2025-09-17", "section": "Business"},
    ]


def test_get_headlines_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/headlines")
    assert response.status_code == 501
    assert "Failed to retrieve data" in response.json()["detail"]


# ----------------------------
# get_trending_now_trends test
# ----------------------------


def test_trending_now_success(mocker):
    mock_trend = type(
        "DailyTrends",
        (),
        {
            "title": "Trend1",
            "ranking": 1,
            "increase_percentage": 10.5,
            "search_volume": 1000,
            "scraped_at": "2025-09-04",
        },
    )()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        mock_trend
    ]
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/trending-now")
    assert response.status_code == 200
    assert response.json() == [
        {
            "title": "Trend1",
            "ranking": 1,
            "increase_percentage": 10.5,
            "search_volume": 1000,
            "scraped_at": "2025-09-04",
        }
    ]


def test_trending_now_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/trending-now")
    assert response.status_code == 501
    assert "Failed to retrieve current trends" in response.json()["detail"]


# --------------------------
# get_keywords_test
# --------------------------


def test_get_keywords_success(mocker):
    # Fake ORM objects
    fake_keywords = type(
        "ArticleKeywords",
        (),
        {
            "keyword_1": "ai",
            "keyword_2": "ml",
            "keyword_3": "nlp",
            "extraction_confidence": 9.5,
        },
    )()
    fake_news = type("News", (), {"headline": "AI breakthrough"})()

    mock_session = make_mock_session(execute_result=[(fake_keywords, fake_news)])
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/keywords")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["headline"] == "AI breakthrough"
    assert data[0]["keyword_1"] == "ai"
    assert data[0]["extraction_confidence"] == 9.5


def test_get_keywords_sqlalchemy_error(mocker):
    mock_session = make_mock_session(execute_side_effect=SQLAlchemyError())
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/keywords")
    assert response.status_code == 501
    assert "Could not retrieve keywords information" in response.json()["detail"]


def test_get_keywords_generic_error(mocker):
    mock_session = make_mock_session(execute_side_effect=Exception("boom"))
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/keywords")
    assert response.status_code == 500
    assert "Unexpected error ocurred" in response.json()["detail"]


# -------------------
# Tests for get_keyword_by_id
# -------------------


def test_get_keyword_by_id_success(mocker):
    fake_keywords = type(
        "ArticleKeywords",
        (),
        {
            "keyword_1": "ai",
            "keyword_2": "ml",
            "keyword_3": "nlp",
            "extraction_confidence": 9.5,
        },
    )()
    fake_news = "AI breakthrough"

    mock_session = make_mock_session(execute_result=[(fake_keywords, fake_news)])
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/keywords/1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["keyword_1"] == "ai"
    assert data[0]["extracion_confidence"] == 9.5
    assert data[0]["headline"] == "AI breakthrough"


def test_get_keyword_by_id_sqlalchemy_error(mocker):
    mock_session = make_mock_session(execute_side_effect=SQLAlchemyError())
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/keywords/1")
    assert response.status_code == 501
    assert (
        "Could not retrieve keywords data from data base" in response.json()["detail"]
    )


def test_get_keyword_by_id_generic_error(mocker):
    mock_session = make_mock_session(execute_side_effect=Exception("kaboom"))
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/keywords/1")
    assert response.status_code == 500
    assert "Unexpected error ocurred" in response.json()["detail"]


# --------------------------
# get_headlines_by_date test
# --------------------------


def test_get_headlines_by_date_success(mocker):
    mock_news = [
        type(
            "News",
            (),
            {
                "id": 1,
                "headline": "Title1",
                "url": "http://url",
                "published_at": "2025-09-17",
            },
        )(),
    ]
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = mock_news
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/headlines/2025-09-17")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["headline"] == "Title1"


def test_get_headlines_by_date_invalid_date():
    response = client.get("/headlines/not-a-date")
    assert response.status_code == 422


def test_get_headlines_by_date_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = Exception()
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/headlines/2025-09-17")
    assert response.status_code == 501
    assert "Failed to retrieve headlines" in response.json()["detail"]


# ------------------------
# post_headline test
# ------------------------


def test_post_single_headline_success(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mocker.patch("api.tracker_api.DataBaseHelper.write_orm_objects", return_value=None)
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    payload = {
        "headline": "Test Headline",
        "url": "http://url",
        "news_section": "Tech",
        "published_at": "2025-09-17T12:00:00",
        "summary": "Summary text",
    }

    response = client.post("/headlines", json=payload)
    assert response.status_code == 201
    assert response.json() == [payload]


def test_post_headline_write_error(mocker):
    mocker.patch(
        "api.tracker_api.DataBaseHelper.write_orm_objects",
        side_effect=SQLAlchemyError(),
    )
    payload = {
        "headline": "Test Headline",
        "url": "http://url",
        "news_section": "Tech",
        "published_at": "2025-09-17T12:00:00",
        "summary": "Summary text",
    }
    response = client.post("/headlines", json=payload)
    assert response.status_code == 501
    assert "Failed to write headlines" in response.json()["detail"]


# ----------------------
# get_news_report test
# ----------------------


def test_get_news_report_success(mocker):
    mock_news = type(
        "News",
        (),
        {
            "headline": "Title",
            "summary": "Some summary",
            "url": "http://url",
            "news_section": "Tech",
        },
    )()
    mock_trends = type(
        "TrendsResults",
        (),
        {"peak_interest": 100, "current_interest": 50, "has_data": True},
    )()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.all.return_value = [(mock_news, mock_trends)]
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/news-report")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["headline"] == "Title"
    assert "peak_interest" in data[0]


def test_get_news_report_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch("api.tracker_api.Session", return_value=mock_session)

    response = client.get("/news-report")
    assert response.status_code == 501
    assert "Failed to retrieve report information" in response.json()["detail"]


def test_google_auth_callback_db_conflict(mocker):
    from exceptions.auth_exceptions import GoogleIDMismatchException

    mocker.patch(
        "api.tracker_api.SecurityService.exchange_code_for_tokens",
        return_value={"id_token": "fake"},
    )
    mocker.patch(
        "api.tracker_api.SecurityService.verify_id_token",
        return_value={"email": "x@example.com", "sub": "g123"},
    )
    mocker.patch(
        "api.tracker_api.DataBaseHelper.check_or_create_user",
        side_effect=GoogleIDMismatchException("Conflict"),
    )

    response = client.post("/auth/google/callback", json={"code": "abc"})
    assert response.status_code == 400
    assert "Conflict" in response.json()["detail"]
