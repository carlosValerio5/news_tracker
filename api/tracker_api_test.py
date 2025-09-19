import pytest
from fastapi.testclient import TestClient
from api.tracker_api import app, DataBaseHelper, logger, SQLAlchemyError
from unittest.mock import MagicMock

client = TestClient(app)

mock_session = MagicMock()
mock_session.__enter__.return_value = mock_session
mock_session.__exit__.return_value = None

# -------------------------
# health_check test
# -------------------------

def test_health_check_available(mocker):
    mocker.patch.object(DataBaseHelper, 'check_database_connection', return_value=None)
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'Status': 'Available'}

def test_health_check_unavailable(mocker):
    mocker.patch.object(DataBaseHelper, 'check_database_connection', side_effect=SQLAlchemyError())
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'Status': 'Unavailable'}

# -----------------------
# get_headlines test
# -----------------------

def test_get_headlines_success(mocker):
    mock_news = [
        type('News', (), {'headline': 'Title1', 'published_at': '2025-09-17', 'news_section': 'Tech'})(),
        type('News', (), {'headline': 'Title2', 'published_at': '2025-09-17', 'news_section': 'Business'})(),
    ]

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = mock_news
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/headlines')
    assert response.status_code == 200
    assert response.json() == [
        {'headline': 'Title1', 'published_at': '2025-09-17', 'section': 'Tech'},
        {'headline': 'Title2', 'published_at': '2025-09-17', 'section': 'Business'},
    ]

def test_get_headlines_db_error(mocker):
    mock_session =MagicMock() 
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/headlines')
    assert response.status_code == 501
    assert 'Failed to retrieve data' in response.json()['detail']

# ----------------------------
# get_trending_now_trends test 
# ----------------------------

def test_trending_now_success(mocker):
    mock_trend = type(
        'DailyTrends', 
        (), 
        {
            'title': 'Trend1',
            'ranking': 1,
            'increase_percentage': 10.5,
            'search_volume': 1000,
            'scraped_at': '2025-09-04'
        }
    )()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_trend]
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/trending-now')
    assert response.status_code == 200
    assert response.json() == [{
        "title": 'Trend1',
        "ranking": 1,
        "increase_percentage": 10.5,
        "search_volume": 1000,
        "scraped_at": '2025-09-04'
    }]

def test_trending_now_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/trending-now')
    assert response.status_code == 501
    assert 'Failed to retrieve current trends' in response.json()['detail']

# --------------------------
# get_headlines_by_date test
# --------------------------

def test_get_headlines_by_date_success(mocker):
    mock_news = [
        type('News', (), {'id': 1, 'headline': 'Title1', 'url': 'http://url', 'published_at': '2025-09-17'})(),
    ]
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = mock_news
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/headlines/2025-09-17')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]['headline'] == 'Title1'

def test_get_headlines_by_date_invalid_date():
    response = client.get('/headlines/not-a-date')
    assert response.status_code == 501
    assert 'Failed to parse date' in response.json()['detail']

def test_get_headlines_by_date_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = Exception()
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/headlines/2025-09-17')
    assert response.status_code == 501
    assert 'Failed to retrieve headlines' in response.json()['detail']

# ------------------------
# post_headline test
# ------------------------


def test_post_single_headline_success(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mocker.patch('api.tracker_api.DataBaseHelper.write_orm_objects', return_value=None)
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    payload = {
        "headline": "Test Headline",
        "url": "http://url",
        "news_section": "Tech",
        "published_at": "2025-09-17T12:00:00",
        "summary": "Summary text"
    }

    response = client.post('/headlines', json=payload)
    assert response.status_code == 201
    assert response.json() == payload

def test_post_headline_write_error(mocker):
    mocker.patch('api.tracker_api.DataBaseHelper.write_orm_objects', side_effect=SQLAlchemyError())
    payload = {
        "headline": "Test Headline",
        "url": "http://url",
        "news_section": "Tech",
        "published_at": "2025-09-17T12:00:00",
        "summary": "Summary text"
    }
    response = client.post('/headlines', json=payload)
    assert response.status_code == 501
    assert 'Failed to write headlines' in response.json()['detail']

# ----------------------
# get_news_report test
# ----------------------

def test_get_news_report_success(mocker):
    mock_news = type('News', (), {'headline': 'Title', 'summary': 'Some summary', 'url': 'http://url'})()
    mock_trends = type('TrendsResults', (), {'peak_interest': 100, 'current_interest': 50, 'has_data': True})()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.all.return_value = [(mock_news, mock_trends)]
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/news-report')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['headline'] == 'Title'
    assert 'peak_intereset' in data[0]

def test_get_news_report_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/news-report')
    assert response.status_code == 501
    assert 'Failed to retrieve report information' in response.json()['detail']

# ------------------------
# get_admin_config test
# ------------------------

def test_get_admin_config_by_id(mocker):
    mock_config = type('AdminConfig', (), {
        'id': 1,
        'target_email': 'test@example.com',
        'summary_send_time': '10:00',
        'last_updated': '2025-09-17'
    })()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_config]
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/admin-config?id=1')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['target_email'] == 'test@example.com'

def test_get_admin_config_by_email(mocker):
    mock_config = type('AdminConfig', (), {
        'id': 2,
        'target_email': 'email@example.com',
        'summary_send_time': '11:00',
        'last_updated': '2025-09-17'
    })()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_config]
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    response = client.get('/admin-config?email=email@example.com')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['target_email'] == 'email@example.com'

def test_get_admin_config_db_error(mocker):
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch('api.tracker_api.Session', return_value=mock_session)

    with pytest.raises(Exception):
        client.get('/admin-config?id=1')