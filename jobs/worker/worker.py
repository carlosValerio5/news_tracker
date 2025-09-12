import logging
from collections.abc import Callable
from aws_handler.sqs import AwsHelper
from sqlalchemy.dialects.postgresql import insert

from database.models import ArticleKeywords, TrendsResults
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
        logger.debug(f"Attempting to insert ArticleKeywords: {article_keywords}")

        # Validate keyword_1 exists
        article_keywords = [
            ak for ak in article_keywords
            if ak.get("keyword_1")
        ]

        if not article_keywords:
            logger.warning("No keywords extracted at WorkerJob.process_messages.")
            return

        try:
            result = DataBaseHelper.write_batch_of_objects_returning(
                ArticleKeywords, 
                self._session_factory, 
                article_keywords, 
                logger, 
                return_columns=[
                    ArticleKeywords.id,
                    ArticleKeywords.keyword_1,
                    ArticleKeywords.keyword_2,
                    ArticleKeywords.keyword_3
                ],
                conflict_index=['composed_query']
                )
        except Exception:
            logger.exception('Failed to write keywords.')
            raise 

        ### Gtrends estimate popularity
        trends_results = self.estimate_popularity(result)

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
            headline = message.get('Body', '')

            if not headline or not headline.strip():
                logger.warning('Failed to process headline, sent to fallback queue.')
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue

            try:
                keywords = self._processor_service.extract_keywords(headline)
            except Exception:
                logger.error('Failed to process headline, sending to fallback queue.')
                self._aws_handler.send_message_to_fallback_queue(message=message)
                continue
            
            article_keywords.append(keywords)

            try:
                self._aws_handler.delete_message_main_queue(message.get('ReceiptHandle', ''))
            except ValueError as e:
                self._aws_handler.send_message_to_fallback_queue(message=message)
                logger.exception(e)
        
        return article_keywords
