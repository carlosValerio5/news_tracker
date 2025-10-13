from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Activity(BaseModel):
    id: int
    activity_type: str
    description: str
    occurred_at: Optional[datetime]
    entity_id: Optional[int]
    entity_type: str

    class Config:
        from_attributes = True


class ActivitiesResponse(BaseModel):
    activities: List[Activity]
    total: int
    limit: int
    offset: int
