'''Admin Router for User Management'''
import os
import re
from datetime import datetime, time
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from database import models
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

class AdminConfig(BaseModel):
    target_email: str
    summary_send_time: time
    last_updated: datetime

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

@admin_router.get("/admin-config")
def get_admin_config(id: Optional[int]=None, email: Optional[str]=None):
    '''
    Gets the admin config for a specific id.

    :param id: Id of admin config.
    '''
    if id:
        stmt = select(models.AdminConfig).filter(models.AdminConfig.id == id)

    elif email:
        stmt = select(models.AdminConfig).filter(models.AdminConfig.target_email == email)

    try:
        with Session(engine) as session:
            results = session.execute(stmt).scalars().all()
    except SQLAlchemyError:
        logger.error('Failed to retrieve admin config data.')
        raise

    return [
        {
            "id": config.id,
            "target_email": config.target_email,
            "summary_send_time": config.summary_send_time,
            "last_updated": config.last_updated,
        }
        for config in results
    ]

@admin_router.post("/admin-config", status_code=201)
def post_admin_config(config: AdminConfig):
    '''
    Posts an admin config entry to the database.

    :param config: AdminConfig object containing config data to be inserted.
    '''
    # Validates there's only an @ symbol before the . symbol
    if not re.match(r"[^@]+@[^@]+\.[^@]+", config.target_email):
        logger.error("Wrong format for email.")
        raise HTTPException(
            status_code=400,
            detail="Invalid format for target email."
        )

    session_factory = lambda : Session(engine)

    config_to_insert = models.AdminConfig(
        target_email = config.target_email,
        summary_send_time = config.summary_send_time,
        last_updated = config.last_updated
    )

    try:
        DataBaseHelper.write_orm_objects(config_to_insert, session_factory, logger)
    except SQLAlchemyError:
        logger.error("Failed to write objects to db.")
        raise HTTPException(
            status_code=501,
            detail="Failed to write orm objects to data base."
        )
    except Exception:
        logger.exception("Exception ocurred during data base write.")
        raise HTTPException(
            status_code=500,
            detail="Unexpedted error ocurred."
        )
    
    return config