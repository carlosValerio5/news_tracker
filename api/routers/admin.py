"""Admin Router for User Management"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, case
from datetime import timedelta, timezone
from pydantic.type_adapter import TypeAdapter
from dataclasses import asdict

from database import models
from database.data_base import engine
from sqlalchemy.orm import Session
from helpers.database_helper import DataBaseHelper
from exceptions.auth_exceptions import UserNotFoundException
from logger.logging_config import logger
from api.auth.scopes import Scope
from api.auth.jwt_service import JWTService
from api.pydantic_models.admin_config import AdminConfig
from api.pydantic_models.activities import Activity, ActivitiesResponse
from cache.redis import RedisService
from exceptions.cache_exceptions import CacheMissError
from cache.activity_dataclass import ActivitiesResponse as ActivitiesResponseDataclass
from cache.activity_dataclass import Activity as ActivityDataClass
from cache.activity_dataclass import ActiveUsersResponse
from cache.activity_dataclass import ReportsGeneratedResponse
from cache.activity_dataclass import NewSignupsResponse

load_dotenv()
security = HTTPBearer()

jwt_secret = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_PASSWORD = REDIS_PASSWORD if REDIS_PASSWORD else None
redis_service = RedisService(host=REDIS_HOST, password=REDIS_PASSWORD, logger=logger)

def session_factory():
    """Factory to create new SQLAlchemy sessions"""
    return Session(engine)


jwt_service = JWTService(secret_key=jwt_secret, algorithm=jwt_algorithm)
type_adapter_Activity = TypeAdapter(ActivityDataClass)


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
    dependencies=[Depends(require_admin)],
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

    config_to_insert = {
        "target_email": config.target_email,
        "summary_send_time": config.summary_send_time,
        "last_updated": config.last_updated,
    }

    try:
        DataBaseHelper.upsert_orm_from_dict(
            models.AdminConfig,
            "target_email",
            config_to_insert,
            session_factory,
            logger,
        )
    except SQLAlchemyError:
        logger.exception("Failed to write objects to db.")
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
        cached_data = redis_service.get_cached_data("active_users", datetime.now(), ActiveUsersResponse)

        if cached_data:
            logger.info("Cache hit for active users.")
            cached_obj = cached_data[0]  # ActiveUsersResponse
            # convert dataclass -> dict
            return asdict(cached_obj)

    except CacheMissError:
        logger.info("No cached active users found.")
    except Exception as e:
        logger.error(f"Error retrieving active users from cache: {e}")

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
            daily_active_count = row.today_window or 0
            weekly_active_count = row.this_week or 0
            prev_week_count = row.prev_week or 0
            diff = (
                ((weekly_active_count - prev_week_count) / prev_week_count * 100)
                if prev_week_count > 0
                else None
            )

            active_users_response = ActiveUsersResponse(
                value_daily=daily_active_count,
                value_weekly=weekly_active_count,
                diff=diff,
            )

            if redis_service:
                # TTL set to 24 hours
                redis_service.set_cached_data("active_users", datetime.now(), active_users_response, expire_seconds=86400)

            return asdict(active_users_response)
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
        cached_data = redis_service.get_cached_data("new_signups", datetime.now(), NewSignupsResponse)

        if cached_data:
            logger.info("Cache hit for new signups.")
            cached_obj = cached_data[0]  # NewSignupsResponse
            # convert dataclass -> dict
            return asdict(cached_obj)

    except CacheMissError:
        logger.info("No cached new signups found.")
    except Exception as e:
        logger.error(f"Error retrieving new signups from cache: {e}")

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

            new_signups_response = NewSignupsResponse(
                value_daily=daily_window,
                value_weekly=this_week,
                diff=((this_week - prev_week) / prev_week * 100)
                if prev_week > 0
                else None,
            )

            if redis_service:
                # TTL set to 24 hours
                redis_service.set_cached_data("new_signups", datetime.now(), new_signups_response, expire_seconds=86400)

            return asdict(new_signups_response)
    except SQLAlchemyError as e:
        logger.error("Failed to retrieve signup information", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to retrieve signup information")
    except Exception as e:
        logger.error("Failed to retrieve signup information", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@admin_router.get("/reports-generated", status_code=200)
async def get_reports_generated():
    """
    Gets the count of reports generated in the current day.

    :return: Dict with counts of reports generated.
    """
    try:
        cached_data = redis_service.get_cached_data("reports_generated", datetime.now(), ReportsGeneratedResponse)

        if cached_data:
            logger.info("Cache hit for reports generated.")
            cached_obj = cached_data[0]  # ReportsGeneratedResponse
            # convert dataclass -> dict
            return asdict(cached_obj)

    except CacheMissError:
        logger.info("No cached reports generated found.")
    except Exception as e:
        logger.error(f"Error retrieving reports generated from cache: {e}")

    try:
        with session_factory() as session:
            # TODO move to helper function
            current_time = datetime.now(tz=timezone.utc)
            current_time = current_time.time()

            stmt_daily = select(func.count().label("count")).filter(
                models.AdminConfig.summary_send_time <= current_time
            )

            daily_report_count = session.execute(stmt_daily).scalar()

            reports_generated_response = ReportsGeneratedResponse(
                value_daily=daily_report_count,
            )

            if redis_service:
                # TTL set to 24 hours
                redis_service.set_cached_data("reports_generated", datetime.now(), reports_generated_response, expire_seconds=86400)

            return asdict(reports_generated_response)
    except SQLAlchemyError as e:
        logger.error("Failed to retrieve report information", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to retrieve report information")
    except Exception as e:
        logger.error("Failed to retrieve report information", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@admin_router.get(
    "/recent-activities", response_model=ActivitiesResponse, status_code=200
)
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    activity_type: Optional[str] = Query(None),
    session_factory=session_factory,
):
    """
    Gets recent activities for the admin dashboard.

    :param limit: Number of recent activities to retrieve (default is 10, max 100).
    :param offset: Number of activities to skip for pagination (default is 0).
    :param activity_type: Optional filter by activity type.
    :return: ActivitiesResponse containing a list of recent activities.
    """
    try:
        cached_data = redis_service.get_cached_data("recent_activities", datetime.now(), ActivitiesResponseDataclass)

        if cached_data:
            logger.info("Cache hit for recent activities.")
            cached_obj = cached_data[0]  # ActivitiesResponseDataclass
            # convert dataclass -> dict, then validate into the Pydantic response model
            return ActivitiesResponse.model_validate(asdict(cached_obj))

    except CacheMissError:
        logger.info("No cached recent activities found.")
    except Exception as e:
        logger.error(f"Error retrieving recent activities from cache: {e}")

    try:
        with session_factory() as session:
            stmt = select(models.RecentActivity)

            if activity_type:
                stmt = stmt.filter(models.RecentActivity.activity_type == activity_type)

            total_stmt = select(func.count()).select_from(stmt.subquery())
            total = session.execute(total_stmt).scalar()

            stmt = (
                stmt.order_by(models.RecentActivity.occurred_at.desc())
                .limit(limit)
                .offset(offset)
            )
            results = session.execute(stmt).scalars().all()

            activities = [type_adapter_Activity.validate_python(activity.__dict__) for activity in results]

            activities_response = ActivitiesResponseDataclass(
                activities=activities, total=total, limit=limit, offset=offset
            )

            if redis_service:
                # TTL set to 1 hour
                redis_service.set_cached_data("recent_activities", datetime.now(), activities_response, expire_seconds=3600)

            return activities_response
    except SQLAlchemyError as e:
        logger.exception(
            "Failed to retrieve report information", extra={"error": str(e)}
        )
        raise HTTPException(
            status_code=500, detail="Failed to retrieve recent activities."
        )
