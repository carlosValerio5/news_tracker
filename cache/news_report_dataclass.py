from dataclasses import dataclass
from typing import List

from cache.news_dataclass import NewsReportData

@dataclass
class NewsReport:
    date: str
    news_items: List[NewsReportData]
    created_at: str