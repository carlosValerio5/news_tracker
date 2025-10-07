'''JWT service for creating and verifying JWTs.'''
from jose import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from api.auth.scopes import Scope
from logger.logging_config import logger
from sqlalchemy.orm import Session

from database.data_base import engine
from database.models import Users


class JWTService:
    '''
    Service for creating and verifying JWTs.
    '''

    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_app_jwt(self, user_info: dict) -> str:
        '''
        Creates a JWT for the authenticated user.

        :param user_info: User dict containing user information (e.g., email).
        '''
        # Normalize role into the Scope enum. Accept either an enum member or the raw value.
        role = user_info.get("role")
        try:
            # If role is already a Scope member this will work, or if it's the raw value (e.g. 'a'/'u')
            scope = Scope(role)
        except Exception:
            # Fallback to USER when role is missing or invalid
            scope = Scope.USER

        payload = {
            "sub": user_info.get("google_id"),
            "email": user_info.get("email"),
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
            "scopes": [scope.value]
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_jwt(self, token: str) -> dict:
        '''
        Decodes and verifies the JWT.

        :param token: JWT string to decode.
        '''
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            logger.exception(f"Invalid token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")