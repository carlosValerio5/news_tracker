from jose import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from api.scopes import Scope
from logger.logging_config import logger




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
        
        :param user_info: Dictionary containing user information (e.g., email, sub).
        '''
        payload = {
            "sub": user_info["sub"],  # Google user ID
            "email": user_info["email"],
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
            "scopes": []
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