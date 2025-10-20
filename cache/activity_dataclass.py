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
