import logging
import json
from collections.abc import Callable
from aws_handler.sqs import AwsHelper
from sqlalchemy.dialects.postgresql import insert

from database.models import ArticleKeywords, TrendsResults, News
from helpers.database_helper import DataBaseHelper 
from jobs.worker.trends_service import GoogleTrendsService
from jobs.worker.nlp_service import HeadlineProcessService

'''Worker module, bussiness logic for headline processing'''

logger = logging.getLogger(__name__)

class WorkerJob():
    '''Worker handling all operations for keyword popularity estimation'''

    def __init__(self, api: GoogleTrendsService, processor_service: HeadlineProcessService, aws_handler: AwsHelper, session_factory: Callable):
        '''
        Initialize the Worker Instance

        :params api: Api handler for popularity estimates
        :processor_service: NLP processor service to extract keywords
        :aws_handler: Instance of aws handler class.
        :session factory: Function to create a db session.
        '''
        self._api = api
        self._processor_service = processor_service
        self._aws_handler = aws_handler
        self._session_factory = session_factory

    def process_messages(self) -> None:
        '''Extracts keywords and saves to ArticleKeywords table'''

        try:
            messages = self._aws_handler.poll_messages()
        except Exception as e:
            logger.warning("Unable to poll for sqs messages.{e}")
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
                    ArticleKeywords.keyword_3
                ],
                conflict_index=['composed_query']
            )
        except Exception:
            logger.exception('Failed to write keywords.')
            raise 

        # map News.keywords_id to respective row in table ArticleKeywords
        session = self._session_factory()
        news_keywords_mapping = self._deduplicate_keywords_news(article_keywords, db_keywords)
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

        ### Gtrends estimate popularity
        trends_results = self.estimate_popularity(db_keywords)

        if not trends_results:
            logger.warning("No trends results extracted at WorkerJob.process_messages.")
            return

        try:
            result = DataBaseHelper.write_batch_of_objects(TrendsResults, self._session_factory, trends_results, logger)
        except Exception:
            logger.exception('Failed to write trends results.')
            raise

    def estimate_popularity(self, result: list[dict]) -> list[dict]:
        '''
        Estimates the popularity of the extracted headlines
        
        :param result: Result of inserted rows in ArticleKeywords
        '''

        trends_results = []
        for row in result:
            id = row.get('id')
            keywords = [row.get('keyword_1', ''), row.get('keyword_2', ''), row.get('keyword_3', '')]

            if not keywords:
                logger.warning("Empty keyword list. (worker.estimate_popularity)")
                continue
            
            try:
                principal_keyword = self._processor_service.get_principal_keyword(keywords)
            except:
                logger.exception('Failed to extract principal keywords.')

            result_trends = self._api.estimate_popularity(principal_keyword)

            if not result_trends:
                logger.error('Failed to estimate popularity for keywords with id %d', id)
                continue

            result_trends['article_keywords_id'] = id

            trends_results.append(result_trends)

        return trends_results

    def process_list_of_messages(self, messages: list) -> list:
        '''
        Iterates over a list of messages and processes headlines

        :param messages: List of messages to process.
        '''
        article_keywords = []
        for message in messages:
            try:
                payload = json.loads(message.get('Body', {}))
            except json.JSONDecodeError:
                logger.warning('Invalid message format, sending to fallback queue.')
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue

            news_id = payload.get('id', '')
            headline = payload.get('headline', '').strip()

            if not news_id or not headline:
                logger.warning('Failed to process headline, sent to fallback queue.')
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue

            try:
                keywords = self._processor_service.extract_keywords(headline)
            except Exception:
                logger.error('Failed to process headline, sending to fallback queue.')
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue
            
            article_keywords.append({
                "news_id": news_id,
                "keyword_1": keywords.get("keyword_1"),
                "keyword_2": keywords.get("keyword_2"),
                "keyword_3": keywords.get("keyword_3"),
                "extraction_confidence": keywords.get("extraction_confidence"),
            })

            try:
                self._aws_handler.delete_message_main_queue(message.get('ReceiptHandle', ''))
            except ValueError as e:
                self._aws_handler.send_message_to_fallback_queue(message=message)
                logger.exception(e)
        
        return article_keywords
            
    def _deduplicate_article_keywords(self, article_keywords: list) -> list[dict]:
        '''
        Deduplicates article keywords entries to insert to data base.
        
        :param article_keywords: List containing the objects to deduplicate.
        '''

        insert_payload = []
        seen = set()
        for entry in article_keywords:
            keywords = [kw.lower() for kw in (entry.get("keyword_1"), entry.get("keyword_2"), entry.get("keyword_3")) if kw]
            composed_query = "|".join(keywords)

            if composed_query in seen:
                continue

            insert_payload.append(
                {k: entry[k] for k in ("keyword_1", "keyword_2", "keyword_3", "extraction_confidence")}
            )

        return insert_payload

    def _deduplicate_keywords_news(self, entries: list, keywords_inserted: list) -> tuple:
        '''
        Deduplicates pair of articlekeywords and news
        
        :param entries: list of entries to deduplicate.
        :param keywords_inserted: List of keywords already inserted and to be mapped.
        '''
        keywords_to_id = {(row["keyword_1"], row["keyword_2"], row["keyword_3"]): row["id"] for row in keywords_inserted}
        seen = set()
        for article_keyword in entries:
            news_id = article_keyword["news_id"]
            keywords_key = (article_keyword["keyword_1"], article_keyword["keyword_2"], article_keyword["keyword_3"])
            keyword_id = keywords_to_id[keywords_key]

            # check for duplicates
            if keyword_id and (keyword_id, news_id) not in seen:
                seen.add((keyword_id, news_id))

        return seen