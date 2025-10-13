from pydantic import BaseModel
from datetime import datetime, time

class AdminConfig(BaseModel):
    target_email: str
    summary_send_time: time
    last_updated: datetime