from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class Activity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_type: str
    description: str
    occurred_at: Optional[datetime]
    entity_id: Optional[int]
    entity_type: str


class ActivitiesResponse(BaseModel):
    activities: List[Activity]
    total: int
    limit: int
    offset: int
