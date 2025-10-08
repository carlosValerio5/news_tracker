import pytest
from fastapi import HTTPException
from datetime import datetime, timezone

import api.auth.jwt_service as jwt_service_module
from api.auth.scopes import Scope


def test_create_app_jwt_with_admin_enum(monkeypatch):
    captured = {}

    def fake_encode(payload, secret_key, algorithm=None):
        # capture payload for assertions
        captured["payload"] = payload
        captured["secret"] = secret_key
        captured["alg"] = algorithm
        return "encoded-token"

    monkeypatch.setattr(jwt_service_module.jwt, "encode", fake_encode)

    svc = jwt_service_module.JWTService(secret_key="s", algorithm="HS256")
    token = svc.create_app_jwt(
        {"google_id": "g1", "email": "e@example.com", "role": Scope.ADMIN}
    )

    assert token == "encoded-token"
    payload = captured["payload"]
    assert payload["sub"] == "g1"
    assert payload["email"] == "e@example.com"
    assert isinstance(payload["exp"], datetime)
    # exp should be timezone-aware UTC
    assert payload["exp"].tzinfo == timezone.utc
    assert payload["scopes"] == [Scope.ADMIN.value]


def test_create_app_jwt_with_raw_role_value(monkeypatch):
    monkeypatch.setattr(
        jwt_service_module.jwt, "encode", lambda payload, s, algorithm=None: "t"
    )

    svc = jwt_service_module.JWTService(secret_key="s", algorithm="HS256")
    token = svc.create_app_jwt({"google_id": "g2", "email": "x@y.com", "role": "a"})

    assert token == "t"


def test_create_app_jwt_with_invalid_role_falls_back_to_user(monkeypatch):
    def fake_encode(payload, s, algorithm=None):
        return payload

    monkeypatch.setattr(jwt_service_module.jwt, "encode", fake_encode)

    svc = jwt_service_module.JWTService(secret_key="s", algorithm="HS256")
    payload = svc.create_app_jwt(
        {"google_id": "g3", "email": "u@u.com", "role": "something-else"}
    )

    # when encode returns payload, ensure scopes fallback to USER
    assert payload["scopes"] == [Scope.USER.value]


def test_decode_jwt_success(monkeypatch):
    monkeypatch.setattr(
        jwt_service_module.jwt,
        "decode",
        lambda token, sk, algorithms=None: {"sub": "g1", "email": "e"},
    )

    svc = jwt_service_module.JWTService(secret_key="s", algorithm="HS256")
    payload = svc.decode_jwt("any-token")
    assert payload["sub"] == "g1"


def test_decode_jwt_expired_raises(monkeypatch):
    # Make decode raise the ExpiredSignatureError from the jose jwt module
    def raise_exp(token, sk, algorithms=None):
        raise jwt_service_module.jwt.ExpiredSignatureError()

    monkeypatch.setattr(jwt_service_module.jwt, "decode", raise_exp)

    svc = jwt_service_module.JWTService(secret_key="s", algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        svc.decode_jwt("t")

    assert exc.value.status_code == 401
    assert "expired" in str(exc.value.detail).lower()


def test_decode_jwt_invalid_raises(monkeypatch):
    def raise_jwt_error(token, sk, algorithms=None):
        raise jwt_service_module.jwt.JWTError("bad")

    monkeypatch.setattr(jwt_service_module.jwt, "decode", raise_jwt_error)

    svc = jwt_service_module.JWTService(secret_key="s", algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        svc.decode_jwt("t")

    assert exc.value.status_code == 401
