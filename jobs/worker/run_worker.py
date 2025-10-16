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
from aws_handler.s3 import S3Handler


def session_factory():
    """Factory to create new SQLAlchemy sessions"""
    return Session(engine)


def run_worker():
    load_dotenv()
    TRENDS_BASE_URL = os.getenv("GOOGLE_TRENDS_URL")
    API_KEY = os.getenv("SERP_API_KEY")
    QUEUE_URL = os.getenv("MAIN_QUEUE_URL")
    FALLBACK_QUEUE_URL = os.getenv("FALLBACK_QUEUE_URL")
    BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    CDN_DOMAIN_NAME = os.getenv("CDN_DOMAIN_NAME")

    google_trends = GoogleTrendsService(TRENDS_BASE_URL, API_KEY)
    nlp_processor = HeadlineProcessService()
    aws_helper = AwsHelper(queue_url=QUEUE_URL, fallback_queue_url=FALLBACK_QUEUE_URL)
    s3_handler = S3Handler(BUCKET_NAME, CDN_DOMAIN_NAME)

    worker = WorkerJob(
        google_trends, nlp_processor, aws_helper, session_factory, s3_handler
    )

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
