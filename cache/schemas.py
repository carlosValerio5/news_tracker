from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Activity:
    id: int
    activity_type: str
    description: str
    occurred_at: Optional[datetime]
    entity_id: Optional[int]
    entity_type: str


@dataclass
class ActivitiesResponse:
    activities: List[Activity]
    total: int
    limit: int
    offset: int


@dataclass
class ActiveUsersResponse:
    value_daily: int
    value_weekly: int
    diff: Optional[float]


@dataclass
class ReportsGeneratedResponse:
    value_daily: int


@dataclass
class NewSignupsResponse:
    value_daily: int
    value_weekly: int
    diff: Optional[float]

@dataclass
class NewsReportData:
    id: str
    headline: str
    summary: str
    url: str
    peak_interest: int
    current_interest: int
    news_section: str
    thumbnail: str | None

@dataclass
class NewsReport:
    date: str
    news_items: List[NewsReportData]
    created_at: str