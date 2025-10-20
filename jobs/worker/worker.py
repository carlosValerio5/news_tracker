import logging
import json
from collections.abc import Callable
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from aws_handler.sqs import AwsHelper
from database.models import ArticleKeywords, TrendsResults, News
from helpers.database_helper import DataBaseHelper
from jobs.worker.trends_service import GoogleTrendsService
from jobs.worker.nlp_service import HeadlineProcessService
from aws_handler.s3 import S3Handler
from exceptions.s3_exceptions import S3BucketServiceError
from exceptions.image_exceptions import ImageDownloadError
from cache.redis import RedisService
from cache.news_dataclass import NewsReportData
from cache.news_report import NewsReport

"""Worker module, bussiness logic for headline processing"""

logger = logging.getLogger(__name__)


class WorkerJob:
    """Worker handling all operations for keyword popularity estimation"""

    def __init__(
        self,
        api: GoogleTrendsService,
        processor_service: HeadlineProcessService,
        aws_handler: AwsHelper,
        session_factory: Callable,
        s3_handler: S3Handler = None,
        redis_service: RedisService = None,
    ):
        """
        Initialize the Worker Instance

        :param api: Api handler for popularity estimates
        :param processor_service: NLP processor service to extract keywords
        :param aws_handler: Instance of aws handler class.
        :param session_factory: Function to create a db session.
        :param s3_handler: Instance of S3Handler to upload thumbnails.
        :param redis_service: Instance of RedisService for caching (optional).
        """
        self._api = api
        self._processor_service = processor_service
        self._aws_handler = aws_handler
        self._session_factory = session_factory
        self._s3_handler = s3_handler
        self._redis_service = redis_service

    def process_messages(self) -> None:
        """Extracts keywords and saves to ArticleKeywords table"""

        try:
            messages = self._aws_handler.poll_messages()
        except Exception as e:
            logger.warning("Unable to poll for sqs messages.", extra={"error": str(e)})
            raise

        article_keywords = self.process_list_of_messages(messages)

        # keep only entries with keyword 1
        article_keywords = [ak for ak in article_keywords if ak.get("keyword_1")]
        if not article_keywords:
            logger.warning("No keywords extracted.")
            return

        insert_payload = self._deduplicate_article_keywords(article_keywords)

        try:
            db_keywords = DataBaseHelper.write_batch_of_objects_and_return(
                ArticleKeywords,
                self._session_factory,
                insert_payload,
                logger,
                return_columns=[
                    ArticleKeywords.id,
                    ArticleKeywords.composed_query,
                    ArticleKeywords.keyword_1,
                    ArticleKeywords.keyword_2,
                    ArticleKeywords.keyword_3,
                ],
                conflict_index=["composed_query"],
            )
        except Exception:
            logger.exception("Failed to write keywords.")
            raise

        # map News.keywords_id to respective row in table ArticleKeywords
        session = self._session_factory()
        news_keywords_mapping = self._deduplicate_keywords_news(
            article_keywords, db_keywords
        )
        try:
            for keyword_id, news_id in news_keywords_mapping:
                session.query(News).filter(News.id == news_id).update(
                    {"keywords_id": keyword_id}
                )
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        # Gtrends estimate popularity
        trends_results = self.estimate_popularity(db_keywords)

        if not trends_results:
            logger.warning("No trends results extracted at WorkerJob.process_messages.")
        else:
            try:
                DataBaseHelper.write_batch_of_objects(
                    TrendsResults, self._session_factory, trends_results, logger
                )
            except Exception:
                logger.exception("Failed to write trends results.")
                raise

        # Cache the aggregated news report after trends estimation
        self._cache_news_report()

    def estimate_popularity(self, result: list[dict]) -> list[dict]:
        """
        Estimates the popularity of the extracted headlines

        :param result: Result of inserted rows in ArticleKeywords
        """

        trends_results = []
        for row in result:
            id = row.get("id")
            keywords = [
                row.get("keyword_1", ""),
                row.get("keyword_2", ""),
                row.get("keyword_3", ""),
            ]

            if not keywords:
                logger.warning("Empty keyword list. (worker.estimate_popularity)")
                continue

            try:
                principal_keyword = self._processor_service.get_principal_keyword(
                    keywords
                )
            except Exception as e:
                logger.exception(
                    "Failed to extract principal keywords.", extra={"error": str(e)}
                )
                continue

            if not principal_keyword:
                logger.warning(
                    "No principal keyword extracted. (worker.estimate_popularity)"
                )
                continue

            result_trends = self._api.estimate_popularity(principal_keyword)

            if not result_trends:
                logger.error(
                    f"Failed to estimate popularity for keywords with id {id}",
                )
                continue

            result_trends["article_keywords_id"] = id

            trends_results.append(result_trends)

        return trends_results

    def process_list_of_messages(self, messages: list) -> list:
        """
        Iterates over a list of messages and processes headlines

        :param messages: List of messages to process.
        """
        article_keywords = []
        for message in messages:
            try:
                payload = json.loads(message.get("Body", {}))
            except json.JSONDecodeError:
                logger.warning("Invalid message format, sending to fallback queue.")
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue

            news_id = payload.get("id", "")
            headline = payload.get("headline", "").strip()
            thumbnail_url = payload.get("thumbnail", "").strip()

            if thumbnail_url and news_id:
                try:
                    s3_url = self._s3_handler.upload_thumbnail(thumbnail_url, news_id)
                    object_to_update = {"thumbnail": s3_url, "id": news_id}

                    DataBaseHelper.update_from_dict(
                        News, "id", object_to_update, self._session_factory, logger
                    )
                except SQLAlchemyError as e:
                    # TODO add delete job for s3 object if db update fails
                    logger.error(f"Failed to update DB for news id {news_id}: {e}")
                except ImageDownloadError as e:
                    logger.error(f"Failed to download image for news id {news_id}: {e}")
                except (Exception, S3BucketServiceError) as e:
                    logger.error(
                        f"Failed to upload thumbnail for news id {news_id}: {e}"
                    )
                    self._aws_handler.send_message_to_fallback_queue(message=message)

            if not news_id or not headline:
                logger.warning("Failed to process headline, sent to fallback queue.")
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue

            try:
                keywords = self._processor_service.extract_keywords(headline)
            except Exception:
                logger.error("Failed to process headline, sending to fallback queue.")
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue

            article_keywords.append(
                {
                    "news_id": news_id,
                    "keyword_1": keywords.get("keyword_1"),
                    "keyword_2": keywords.get("keyword_2"),
                    "keyword_3": keywords.get("keyword_3"),
                    "extraction_confidence": keywords.get("extraction_confidence"),
                }
            )

            try:
                self._aws_handler.delete_message_main_queue(
                    message.get("ReceiptHandle", ""), message.get("MessageId", "")
                )
            except ValueError as e:
                self._aws_handler.send_message_to_fallback_queue(message=message)
                logger.exception(e)

        return article_keywords

    def _deduplicate_article_keywords(self, article_keywords: list) -> list[dict]:
        """
        Deduplicates article keywords entries to insert to data base.

        :param article_keywords: List containing the objects to deduplicate.
        """

        insert_payload = []
        seen = set()
        for entry in article_keywords:
            keywords = [
                kw.lower()
                for kw in (
                    entry.get("keyword_1"),
                    entry.get("keyword_2"),
                    entry.get("keyword_3"),
                )
                if kw
            ]
            composed_query = "|".join(keywords)

            if composed_query in seen:
                continue

            seen.add(composed_query)

            insert_payload.append(
                {
                    k: entry[k]
                    for k in (
                        "keyword_1",
                        "keyword_2",
                        "keyword_3",
                        "extraction_confidence",
                    )
                }
            )

        return insert_payload

    def _deduplicate_keywords_news(
        self, entries: list, keywords_inserted: list
    ) -> tuple:
        """
        Deduplicates pair of articlekeywords and news

        :param entries: list of entries to deduplicate.
        :param keywords_inserted: List of keywords already inserted and to be mapped.
        """
        keywords_to_id = {
            (row["keyword_1"], row["keyword_2"], row["keyword_3"]): row["id"]
            for row in keywords_inserted
        }
        seen = set()
        for article_keyword in entries:
            news_id = article_keyword["news_id"]
            keywords_key = (
                article_keyword["keyword_1"],
                article_keyword["keyword_2"],
                article_keyword["keyword_3"],
            )
            keyword_id = keywords_to_id[keywords_key]

            # check for duplicates
            if keyword_id and (keyword_id, news_id) not in seen:
                seen.add((keyword_id, news_id))

        return seen

    def _cache_news_report(self) -> None:
        """
        Fetches all news with trends data and caches the aggregated report.
        Uses retry logic with graceful fallback: logs and continues if caching fails.
        Only caches if Redis service is available.
        """
        if not self._redis_service:
            logger.debug("Redis service not available, skipping cache.")
            return

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            session = self._session_factory()
            try:
                # Eagerly load keywords and trends to avoid lazy-load issues after session closes
                news_records = (
                    session.query(News)
                    .options(joinedload(News.keywords).joinedload(ArticleKeywords.trends_result))
                    .where(News.published_at >= today)
                    .all()
                )

                if not news_records:
                    logger.warning("No news records to cache.")
                    return

                # Convert News records to NewsReportData instances while session is active
                news_report_items = []
                for news in news_records:
                    # Access trends through the keyword relationship (already loaded)
                    trends = news.keywords.trends_result if news.keywords else None

                    item = NewsReportData(
                        id=str(news.id),
                        headline=news.headline,
                        summary=news.summary,
                        url=news.url,
                        peak_interest=trends.peak_interest if trends and hasattr(trends, "peak_interest") else 0,
                        current_interest=trends.current_interest if trends and hasattr(trends, "current_interest") else 0,
                        news_section=news.news_section,
                        thumbnail=news.thumbnail,
                    )
                    news_report_items.append(item)

                # Create NewsReport and cache it
                today = datetime.now().strftime("%Y-%m-%d")
                news_report = NewsReport(
                    date=today,
                    news_items=news_report_items,
                    created_at=datetime.now().isoformat(),
                )

                # Attempt to cache with retry on first failure
                self._cache_with_retry(news_report, today)

            finally:
                session.close()

        except Exception as e:
            logger.error(
                f"Failed to prepare news report for caching: {e}",
                exc_info=True,
            )

    def _cache_with_retry(self, news_report: NewsReport, date: str) -> None:
        """
        Attempts to cache the news report with one retry.
        Logs and continues if both attempts fail.

        :param news_report: The NewsReport instance to cache.
        :param date: The date string (YYYY-MM-DD) for the cache key.
        """
        # Check if data is already cached for today
        cache_key = self._redis_service._get_cache_key("daily_news_report", 
                                                        datetime.strptime(date, "%Y-%m-%d"))
        if self._redis_service.get_value(cache_key):
            logger.info(f"News report already cached for {date}, skipping cache write.")
            return
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                # Cache the list of NewsReportData items (news_report.news_items)
                self._redis_service.set_cached_data(
                    key="daily_news_report",
                    date=datetime.strptime(date, "%Y-%m-%d"),
                    data=news_report.news_items,
                    expire_seconds=28800,  # 8 hours
                )
                logger.info(
                    f"Successfully cached news report for {date} with {len(news_report.news_items)} items."
                )
                return
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Cache attempt {attempt} failed, retrying: {e}"
                    )
                else:
                    logger.error(
                        f"Failed to cache news report after {max_retries} attempts: {e}. "
                        "Continuing without cache.",
                        exc_info=True,
                    )
