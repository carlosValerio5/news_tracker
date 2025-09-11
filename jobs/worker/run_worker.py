import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import logging

from worker import WorkerJob
from trends_service import GoogleTrendsService
from nlp_service import HeadlineProcessService
from aws_handler.sqs import AwsHelper
from database.data_base import engine

logger = logging.getLogger(__name__)

def run_worker():
    load_dotenv()
    trends_base_url = os.getenv('GOOGLE_TRENDS_URL')
    api_key = os.getenv('SERP_API_KEY')
    queue_url = os.getenv('MAIN_QUEUE_URL')
    fallback_queue_url = os.getenv('FALLBACK_QUEUE_URL')

    google_trends = GoogleTrendsService(trends_base_url, api_key)
    nlp_processor = HeadlineProcessService()
    aws_helper = AwsHelper(queue_url=queue_url, fallback_queue_url=fallback_queue_url)
    session_factory = lambda: Session(engine)

    worker = WorkerJob(google_trends, nlp_processor, aws_helper, session_factory)

    while True:
        try:
            worker.process_messages()
        except Exception:
            logger.exception('Failed to process message.') # If processing fails next set of messages is processed