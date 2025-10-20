from dataclasses import dataclass


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
