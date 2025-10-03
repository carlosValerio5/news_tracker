from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

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
            "exp": datetime.now() + timedelta(hours=1),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token