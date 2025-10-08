from jobs.trends.trends_scraper import run_scraping_job_trends
from logger.logging_config import logger

"""Main lambda handler for bbc scraper, this file will be located at root level in docker image"""


def lambda_handler(event, context):
    try:
        run_scraping_job_trends()
        logger.info("Trends scraping Lambda executed successfully")
        return {"statusCode": 200, "message": "Script run successfully"}
    except Exception as e:
        logger.exception("Error during trends scraping Lambda execution")
        return {"statusCode": 500, "message": str(e)}
