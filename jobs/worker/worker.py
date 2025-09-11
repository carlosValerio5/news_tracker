import logging
from collections.abc import Callable
from aws_handler.sqs import AwsHelper
from sqlalchemy.dialects.postgresql import insert

from database.models import ArticleKeywords
from helpers.database_helper import DataBaseHelper 
from trends_service import GoogleTrendsService
from nlp_service import HeadlineProcessService

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

        if not article_keywords:
            logger.warning("No keywords extracted at WorkerJob.process_messages.")
            return

        try:
            result = DataBaseHelper.write_batch_of_objects(ArticleKeywords, self._session_factory, article_keywords, logger)
        except Exception:
            logger.exception('Failed to write keywords.')
            raise 

        ### Gtrends estimate popularity


    def estimate_popularity(self, article_keywords):
        '''Estimates the popularity of the extracted headlines'''

        trends_results = []
        for news_article in article_keywords:
            current, average, peak = self._api.estimate_popularity(news_article)

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

    def get_messages(self):
        pass

    def delete_messages(self):
        pass

    def rate_headlines(self):
        pass
