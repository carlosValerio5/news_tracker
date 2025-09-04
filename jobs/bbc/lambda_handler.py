from jobs.bbc.scraper import start_scraping_job

'''Main lambda handler for bbc scraper, this file will be located at root level in docker image'''
def lambda_handler(event, context):

    start_scraping_job()

    return {
        "statusCode": 200,
        "message": "Script run successfully"
    }