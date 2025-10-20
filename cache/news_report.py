from dataclasses import dataclass
from datetime import datetime
from cache.news_dataclass import NewsReportData


@dataclass
class NewsReport:
    """Aggregated daily news report containing a list of news items and metadata."""
    
    date: str  # YYYY-MM-DD format
    news_items: list[NewsReportData]
    created_at: str  # ISO timestamp
    
    def __post_init__(self):
        """Validate that news_items is a list of NewsReportData."""
        if not isinstance(self.news_items, list):
            raise ValueError("news_items must be a list")
        if not all(isinstance(item, NewsReportData) for item in self.news_items):
            raise ValueError("All items in news_items must be NewsReportData instances")
