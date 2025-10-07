from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.routers.admin import admin_router
import api.routers.admin as admin_module
from unittest.mock import MagicMock

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