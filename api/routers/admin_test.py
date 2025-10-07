import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.routers.admin import admin_router
import api.routers.admin as admin_module
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

from helpers.database_helper import DataBaseHelper

# Create a FastAPI app and include the admin router so TestClient can exercise routes
app = FastAPI()
app.include_router(admin_router)
client = TestClient(app)

# Utility: create a mocked Session context manager
def make_mock_session(execute_result=None, scalars_result=None, execute_side_effect=None):
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
# --------------------------
# Admin router tests
# --------------------------

def test_create_admin_user_success(mocker):
    # Override FastAPI dependency to simulate an admin user and patch DB create_admin
    # Override the get_current_user dependency defined in the admin router module
    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

    # Patch the DataBaseHelper.create_admin that admin_router calls
    # The admin router imports DataBaseHelper from helpers.database_helper
    mocker.patch('helpers.database_helper.DataBaseHelper.create_admin', return_value={'email': 'admin@example.com'})

    response = client.post('/admin/', json={'email': 'admin@example.com'})

    # Clear overrides after request
    client.app.dependency_overrides.pop(admin_module.get_current_user, None)

    assert response.status_code == 201
    assert 'now an admin' in response.json().get('detail', '')

# ------------------------
# get_admin_config test
# ------------------------

def test_get_admin_config_by_id(mocker):

    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

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
    mocker.patch('api.routers.admin.Session', return_value=mock_session)

    response = client.get('/admin/admin-config?id=1')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['target_email'] == 'test@example.com'

def test_get_admin_config_by_email(mocker):

    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

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
    mocker.patch('api.routers.admin.Session', return_value=mock_session)

    response = client.get('/admin/admin-config?email=email@example.com')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['target_email'] == 'email@example.com'

def test_get_admin_config_db_error(mocker):

    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.execute.side_effect = SQLAlchemyError()
    mocker.patch('api.routers.admin.Session', return_value=mock_session)

    with pytest.raises(Exception):
        client.get('/admin/admin-config?id=1')

# ----------------------
# post_admin_config test
# ----------------------

# ------------------
# 1. Happy Path Test
# ------------------
def test_post_admin_config_success(mocker):

    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}
    # Mock DB write function to behave normally
    mocker.patch.object(DataBaseHelper, "write_orm_objects", return_value=None)

    payload = {
        "target_email": "test@example.com",
        "summary_send_time": "12:00:00",
        "last_updated": "2025-09-17T00:00:00"
    }

    response = client.post("/admin/admin-config", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["target_email"] == payload["target_email"]
    assert data["summary_send_time"] == payload["summary_send_time"]


# --------------------------
# 2. Invalid Email Format
# --------------------------
def test_post_admin_config_invalid_email():
    
    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

    payload = {
        "target_email": "invalid-email-format",
        "summary_send_time": "12:00:00",
        "last_updated": "2025-09-17T00:00:00"
    }

    response = client.post("/admin/admin-config", json=payload)
    assert response.status_code == 400
    assert "Invalid format" in response.json()["detail"]


# -------------------------------------------
# 3. SQLAlchemyError during DB write
# -------------------------------------------
def test_post_admin_config_sqlalchemy_error(mocker):

    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

    mocker.patch.object(DataBaseHelper, "write_orm_objects", side_effect=SQLAlchemyError("DB error"))

    payload = {
        "target_email": "test@example.com",
        "summary_send_time": "12:00:00",
        "last_updated": "2025-09-17T00:00:00"
    }

    response = client.post("/admin/admin-config", json=payload)
    assert response.status_code == 501
    assert "Failed to write orm objects" in response.json()["detail"]


# -------------------------------------------
# 4. Unexpected Exception during DB write
# -------------------------------------------
def test_post_admin_config_unexpected_error(mocker):

    client.app.dependency_overrides[admin_module.get_current_user] = lambda: {'scopes': ['a']}

    mocker.patch.object(DataBaseHelper, "write_orm_objects", side_effect=Exception("Unexpected error"))

    payload = {
        "target_email": "test@example.com",
        "summary_send_time": "12:00:00",
        "last_updated": "2025-09-17T00:00:00"
    }

    response = client.post("/admin/admin-config", json=payload)
    assert response.status_code == 500
    assert "Unexpedted error ocurred" in response.json()["detail"]