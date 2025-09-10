import logging
from collections.abc import Callable
from aws_handler.sqs import AwsHelper
from sqlalchemy.dialects.postgresql import insert
import spacy

from database.models import ArticleKeywords
from helpers.database_helper import DataBaseHelper 

'''Worker module, bussiness logic for headline processing'''


logger = logging.getLogger(__name__)

class HeadlineProcessService:
    '''Handles bussiness logic for natural language processing'''

    POS_WEIGHTS = {
        "PROPN": 2.0,
        "NOUN": 1.5,
        "ADJ": 1.0
    }


    def __init__(self, model="en_core_web_sm"):
        '''
        Initialize a Headline Processing Service instance

        :param aws_handler: Instance of Aws handler class to get sqs logic.
        :param model: Name of the model to retrieve from spacy.
        '''
        self._nlp = spacy.load(model, disable=['ner', 'parser'])

    def extract_keywords(self, headline: str) -> dict:
        '''
        Uses NLP algorithms to extract at most 3 keywords per headline 

        :param headline: Headline to be processed. 
        '''

        try:
            keywords = self.process_headline(headline)

        except Exception:
            raise Exception('Failed to process headline.')


        extraction_confidence = self._get_total_confidence(keywords)

        article_keyword ={
            'keyword_1' : keywords[0][0] if len(keywords) > 0 else None,
            'keyword_2' : keywords[1][0] if len(keywords) > 1 else None,
            'keyword_3' : keywords[2][0] if len(keywords) > 2 else None,
            'composed_query' : "".join(kw for kw, _ in keywords),
            'extraction_confidence' : extraction_confidence 
        }
        
        return article_keyword


    def _get_total_confidence(self, keywords: list) -> float:
        '''
        Calculates the total cofidence for a set of keywords

        :param keywords: List of keywords to calculate confidence
        '''
        extraction_confidence = sum(confidence for _, confidence in keywords)
        return round(extraction_confidence, 2)


    def get_level_of_confidence(self, pos: str, index: int) -> float:
        '''
        Gets the level of confidence related to the extracted keywords.

        :param pos: The type of token for this keyword. 
        :param index: The index where the keyword can be found.
        '''
        pos_score = self.POS_WEIGHTS[pos]
        position_score = 1 / (index+1) # earlier tokens get higher weight

        return pos_score + position_score
        

    def process_headline(self, headline: str, max_keywords: int = 3) -> list:
        '''
        Processes a single headline and extracts keywords based in level of confidence

        :param headline: The headline to extract keywords from.
        :param max_keywords: The number of keywords to extract.
        '''
        doc = self._nlp(headline)
        seen = set()
        keywords = []

        for idx, token in enumerate(doc):
            if token.pos_ in self.POS_WEIGHTS and token.is_alpha: # Keep only proper nouns and nouns
                kw = token.lemma_.lower()
                if kw not in seen:
                    seen.add(kw)
                    confidence = self.get_level_of_confidence(kw, token.pos_, idx)
                    keywords.append((kw, confidence))
                
        keywords.sort(key=lambda x: x[1], reverse=True)

        return [(kw.capitalize(), score) for kw, score in keywords[:max_keywords]]


class GoogleTrendsService:
    '''API service, handles bussiness logic for google trends API'''
    def __init__(self, base_url: str, api_key: str):
        '''
        Initialize a Google Trends Client

        :params base_url: The base url for the Google Trends Rating Endpoint
        :api_key: Api key to access SerpApi's service
        '''
        self._base_url = base_url
        self._api_key = api_key

    def estimate_popularity(self, news_article) -> tuple:
        '''
        Estimates the popularity of one news_article

        :param news_article: Article whom will have its popularity estimated.
        '''
        pass




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
