'''Admin Router for User Management'''
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

from database.data_base import engine
from sqlalchemy.orm import Session
from helpers.database_helper import DataBaseHelper
from exceptions.auth_exceptions import UserNotFoundException
from logger.logging_config import logger
from api.auth.scopes import Scope
from api.auth.jwt_service import JWTService

load_dotenv()
security = HTTPBearer()

jwt_secret = os.getenv('JWT_SECRET_KEY')
jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')

jwt_service = JWTService(
    secret_key=jwt_secret,
    algorithm=jwt_algorithm
)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Get current user from JWT token"""
    try:
        payload = jwt_service.decode_jwt(credentials.credentials)
        return payload
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

def require_scopes(*required_scopes: str):
    """Factory for scope-checking dependencies"""
    def check_scopes(user: dict = Depends(get_current_user)) -> dict:
        user_scopes = user.get("scopes", [])
        if not all(scope in user_scopes for scope in required_scopes):
            logger.warning(f"Access denied. User scopes: {user_scopes}, Required: {required_scopes}")
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return user
    return check_scopes


require_admin = require_scopes(Scope.ADMIN.value)
require_read = require_scopes(Scope.USER.value)


admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)

@admin_router.post("/")
def create_admin_user(user_info: dict):
    '''
    Creates an admin user.

    :param user_info: Dict containing user information (e.g., email).
    '''
    email = user_info.get("email")
    if not email:
        logger.error("Email is required to create admin user.")
        raise HTTPException(status_code=400, detail="Email is required.")

    session_factory = lambda: Session(engine)

    try:
        user = DataBaseHelper.create_admin(email, session_factory, logger)
    except UserNotFoundException as e:
        logger.error(f"User not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to check or create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to process user information.")

    return JSONResponse(status_code=201, content={"detail": f"User {user['email']} is now an admin."})

@admin_router.get("/")
def verify_admin():
    '''
    Verifies admin access.
    '''
    return JSONResponse(status_code=200, content={"detail": "Admin access verified."})