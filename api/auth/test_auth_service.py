import pytest
from fastapi import HTTPException

import api.auth.auth_service as auth_service


class DummyResponse:
    def __init__(self, status_code=200, json_payload=None, text=""):
        self.status_code = status_code
        self._json = json_payload or {}
        self.text = text

    def json(self):
        return self._json


def test_exchange_code_for_tokens_success(monkeypatch):
    captured = {}

    def fake_post(url, data):
        # capture values passed to requests.post for assertion
        captured["url"] = url
        captured["data"] = data
        return DummyResponse(
            status_code=200, json_payload={"access_token": "a", "id_token": "i"}
        )

    monkeypatch.setattr(auth_service.req_lib, "post", fake_post)

    result = auth_service.SecurityService.exchange_code_for_tokens(
        code="the-code",
        client_id="cid",
        client_secret="csecret",
        redirect_uri="https://app/cb",
    )

    assert result == {"access_token": "a", "id_token": "i"}
    assert captured["url"] == "https://oauth2.googleapis.com/token"
    # ensure the payload contains the provided values
    assert captured["data"]["code"] == "the-code"
    assert captured["data"]["client_id"] == "cid"


def test_exchange_code_for_tokens_failure(monkeypatch):
    def fake_post(url, data):
        return DummyResponse(status_code=400, text="bad request")

    monkeypatch.setattr(auth_service.req_lib, "post", fake_post)

    with pytest.raises(HTTPException) as excinfo:
        auth_service.SecurityService.exchange_code_for_tokens("x", "cid", "cs", "r")

    assert excinfo.value.status_code == 400


def test_verify_id_token_success(monkeypatch):
    # Prepare a fake payload that the google library would return
    fake_payload = {"sub": "123", "email": "user@example.com"}

    def fake_verify(token, req, audience, clock_skew_in_seconds=0):
        # ensure arguments are forwarded correctly
        assert token == "idtoken"
        assert audience == "cid"
        return fake_payload

    monkeypatch.setattr(auth_service.id_token, "verify_oauth2_token", fake_verify)

    result = auth_service.SecurityService.verify_id_token("idtoken", "cid")
    assert result == fake_payload


def test_verify_id_token_invalid_raises(monkeypatch):
    def fake_verify(token, req, audience, clock_skew_in_seconds=0):
        raise ValueError("invalid")

    monkeypatch.setattr(auth_service.id_token, "verify_oauth2_token", fake_verify)

    with pytest.raises(HTTPException) as excinfo:
        auth_service.SecurityService.verify_id_token("bad", "cid")

    assert excinfo.value.status_code == 401
