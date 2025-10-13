"""Admin Router for User Management"""

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
from sqlalchemy import select, func, case
from datetime import timedelta, timezone

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

jwt_secret = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")


def session_factory():
    """Factory to create new SQLAlchemy sessions"""
    return Session(engine)


jwt_service = JWTService(secret_key=jwt_secret, algorithm=jwt_algorithm)


class AdminConfig(BaseModel):
    target_email: str
    summary_send_time: time
    last_updated: datetime


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
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
            logger.warning(
                f"Access denied. User scopes: {user_scopes}, Required: {required_scopes}"
            )
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return user

    return check_scopes


require_admin = require_scopes(Scope.ADMIN.value)
require_read = require_scopes(Scope.USER.value)


admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    #dependencies=[Depends(require_admin)],
)


@admin_router.post("/")
def create_admin_user(user_info: dict):
    """
    Creates an admin user.

    :param user_info: Dict containing user information (e.g., email).
    """
    email = user_info.get("email")
    if not email:
        logger.error("Email is required to create admin user.")
        raise HTTPException(status_code=400, detail="Email is required.")

    try:
        user = DataBaseHelper.create_admin(email, session_factory, logger)
    except UserNotFoundException as e:
        logger.error(f"User not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to check or create user: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process user information."
        )

    return JSONResponse(
        status_code=201, content={"detail": f"User {user['email']} is now an admin."}
    )


@admin_router.get("/")
def verify_admin():
    """
    Verifies admin access.
    """
    return JSONResponse(status_code=200, content={"detail": "Admin access verified."})


@admin_router.get("/admin-config")
def get_admin_config(id: Optional[int] = None, email: Optional[str] = None):
    """
    Gets the admin config for a specific id.

    :param id: Id of admin config.
    """
    if id:
        stmt = select(models.AdminConfig).filter(models.AdminConfig.id == id)

    elif email:
        stmt = select(models.AdminConfig).filter(
            models.AdminConfig.target_email == email
        )

    try:
        with Session(engine) as session:
            results = session.execute(stmt).scalars().all()
    except SQLAlchemyError:
        logger.error("Failed to retrieve admin config data.")
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
    """
    Posts an admin config entry to the database.

    :param config: AdminConfig object containing config data to be inserted.
    """
    # Validates there's only an @ symbol before the . symbol
    if not re.match(r"[^@]+@[^@]+\.[^@]+", config.target_email):
        logger.error("Wrong format for email.")
        raise HTTPException(status_code=400, detail="Invalid format for target email.")

    config_to_insert = models.AdminConfig(
        target_email=config.target_email,
        summary_send_time=config.summary_send_time,
        last_updated=config.last_updated,
    )

    try:
        DataBaseHelper.write_orm_objects(config_to_insert, session_factory, logger)
    except SQLAlchemyError:
        logger.error("Failed to write objects to db.")
        raise HTTPException(
            status_code=501, detail="Failed to write orm objects to data base."
        )
    except Exception:
        logger.exception("Exception ocurred during data base write.")
        raise HTTPException(status_code=500, detail="Unexpedted error ocurred.")

    return config

@admin_router.get("/active-users", status_code=200)
async def get_active_users():
    """
    Gets the count of active users in the last week and day. 

    :return: Dict with counts of active users.
    """
    try:
        with session_factory() as session:
            # TODO move to helper function
            one_day_ago = datetime.now(tz=timezone.utc) - timedelta(days=1)
            one_week_ago = datetime.now(tz=timezone.utc) - timedelta(weeks=1)
            two_weeks_ago = datetime.now(tz=timezone.utc) - timedelta(weeks=2)

            # helpers to keep the SQL construction readable
            col = models.Users.last_login

            def when_tuple(cond):
                """Return a when-tuple for use with case()."""
                return (cond, 1)

            this_week_case = case(when_tuple(col >= one_week_ago), else_=0)
            prev_week_cond = (col >= two_weeks_ago) & (col < one_week_ago)
            prev_week_case = case(when_tuple(prev_week_cond), else_=0)
            today_case = case(when_tuple(col >= one_day_ago), else_=0)

            stmt = select(
                func.sum(this_week_case).label("this_week"),
                func.sum(prev_week_case).label("prev_week"),
                func.sum(today_case).label("today_window"),
            )

            row = session.execute(stmt).one() 
            daily_active_count = (row.today_window or 0)
            weekly_active_count = (row.this_week or 0)
            prev_week_count = (row.prev_week or 0)
            diff = ((weekly_active_count - prev_week_count) / prev_week_count * 100) if prev_week_count > 0 else None

            return {
                "daily_active_users": daily_active_count,
                "weekly_active_users": weekly_active_count,
                "prev_week_users": diff,
            }
    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve active user counts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active users.")

@admin_router.get("/new-signups", status_code=200)
async def get_new_signups():
    """
    Gets the count of new user signups in the last week and day.

    :return: Dict with counts of new signups.
    """
    try:
        with session_factory() as session:
            # TODO move to helper function
            one_day_ago = datetime.now(tz=timezone.utc) - timedelta(days=1)
            one_week_ago = datetime.now(tz=timezone.utc) - timedelta(weeks=1)
            two_weeks_ago = datetime.now(tz=timezone.utc) - timedelta(weeks=2)

            # use helpers and clear grouping for readability (mirror get_active_users)
            col = models.Users.created_at

            def when_tuple(cond):
                return (cond, 1)

            this_week_case = case(when_tuple(col >= one_week_ago), else_=0)
            prev_week_cond = (col >= two_weeks_ago) & (col < one_week_ago)
            prev_week_case = case(when_tuple(prev_week_cond), else_=0)
            today_case = case(when_tuple(col >= one_day_ago), else_=0)

            stmt = select(
                func.sum(this_week_case).label("this_week"),
                func.sum(prev_week_case).label("prev_week"),
                func.sum(today_case).label("today_window"),
            )

            row = session.execute(stmt).one()
            this_week = int(row.this_week or 0)
            prev_week = int(row.prev_week or 0)
            daily_window = int(row.today_window or 0)

            return {
                "daily_signup_count": daily_window,
                "weekly_signup_count": this_week,
                "weekly_signup_diff": ((this_week - prev_week) / prev_week * 100) if prev_week > 0 else None,
            }
    except SQLAlchemyError as e:
        logger.error('Failed to retrieve signup information', extra={'error': str(e)})
        return JSONResponse(status_code=501, content="Failed to retrieve signup information")
    except Exception as e:
        logger.error('Failed to retrieve signup information', extra={'error': str(e)})
        return JSONResponse(status_code=501, content="Unexpected error ocurred")
    
@admin_router.get('/reports-generated', status_code=200)
async def get_reports_generated():
    """
    Gets the count of reports generated in the current day.
    
    :return: Dict with counts of reports generated.
    """
    try:
        with session_factory() as session:
            # TODO move to helper function
            current_time = datetime.now(tz=timezone.utc)
            current_time = current_time.time()

            stmt_daily = select(func.count().label("count")).filter(
                models.AdminConfig.summary_send_time <= current_time
            )

            daily_report_count = session.execute(stmt_daily).scalar()

            return {
                "daily_report_count": daily_report_count,
            }
    except SQLAlchemyError as e:
        logger.error('Failed to retrieve report information', extra={'error': str(e)})
        return JSONResponse(status_code=501, content="Failed to retrieve report information")
    except Exception as e:
        logger.error('Failed to retrieve report information', extra={'error': str(e)})
        return JSONResponse(status_code=501, content="Unexpected error occurred")