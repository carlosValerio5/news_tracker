import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from logger.logging_config import logger
from botocore.exceptions import NoCredentialsError

from jobs.worker.worker import WorkerJob
from jobs.worker.trends_service import GoogleTrendsService
from jobs.worker.nlp_service import HeadlineProcessService
from aws_handler.sqs import AwsHelper
from database.data_base import engine


def session_factory():
    """Factory to create new SQLAlchemy sessions"""
    return Session(engine)


def run_worker():
    load_dotenv()
    trends_base_url = os.getenv("GOOGLE_TRENDS_URL")
    api_key = os.getenv("SERP_API_KEY")
    queue_url = os.getenv("MAIN_QUEUE_URL")
    fallback_queue_url = os.getenv("FALLBACK_QUEUE_URL")

    google_trends = GoogleTrendsService(trends_base_url, api_key)
    nlp_processor = HeadlineProcessService()
    aws_helper = AwsHelper(queue_url=queue_url, fallback_queue_url=fallback_queue_url)

    worker = WorkerJob(google_trends, nlp_processor, aws_helper, session_factory)

    while True:
        try:
            worker.process_messages()
        except NoCredentialsError:
            logger.exception("Failed to get aws credentials.")
            return
        except Exception:
            logger.exception(
                "Failed to process message."
            )  # If processing fails next set of messages is processed


if __name__ == "__main__":
    run_worker()
