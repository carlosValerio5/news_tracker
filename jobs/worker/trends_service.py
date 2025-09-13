import json
import requests
from datetime import datetime, date
from requests import HTTPError
from logging import getLogger

'''Google Trend handler module, class and methods to estimate popularity'''

logger = getLogger(__name__)
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

    def estimate_popularity(self, keyword: str) -> (dict|None):
        '''
        Estimates the popularity for a given keyword string.

        :param keyword: keyword string whom will have its popularity estimated.
        '''
        try:
            payload = self.get_api_payload(keyword)
        except HTTPError:
            logger.exception('Failed to make request to %s', self._base_url)
            return
        except Exception:
            logger.exception('Unexpected error ocurred.')
            return

        current_interest = self.get_current_interest(payload)
        peak_interest = self.get_peak_interest(payload)

        try:
            start_date, end_date = self.get_start_end_date(payload)
        except KeyError:
            logger.exception('Failed to get date period data.')
            return None

        logger.info('Current interest %d\nPeak interest: %d', current_interest, peak_interest)
        # return (current_interest, peak_interest)


        has_data = True
        if current_interest == -1 and peak_interest == -1:
            has_data = False

        trends_results = {
            'article_keywords_id': int(),
            'has_data' : has_data,
            'peak_interest': peak_interest,
            'current_interest': current_interest,
            'data_period_start': start_date,
            'data_period_end': end_date
        }

        return trends_results


    def get_api_payload(self, keyword: str) -> tuple:
        '''
        Makes an api request for a single keyword.

        :param keyword: Keyword included in query.
        '''
        if not keyword or not keyword.strip():
            raise ValueError('keyword required')

        try:
            r = requests.get(self._base_url, params={'api_key': self._api_key, 'q':keyword, 'engine':'google_trends'}, timeout=(3, 10))
            r.raise_for_status()
        except HTTPError:
            logger.exception('Failed to make request.')
            raise
        except Exception:
            logger.warning('Unexpected error ocurred.')
            raise

        return json.loads(r.text)
        
    def get_peak_interest(self, payload: dict) -> int:
        '''
        Gets the peak interest for a given keyword.

        :param payload: Dict with timeline data including interest.
        '''

        interest_over_time = payload.get('interest_over_time', [])
        if not interest_over_time:
            logger.warning('Could not extract interest over time data.')
            return -1

        timeline_data = interest_over_time.get('timeline_data', []) 
        if not timeline_data:
            logger.warning('Could not extract timeline data.')
            return -1

        max_interest = -1
        for entry in timeline_data:
            values = entry.get('values')

            if not values:
                logger.warning('No data for date %s', entry.get('date'))
                continue

            for value_entry in values:
                interest = value_entry.get('extracted_value')
                max_interest = max(max_interest, interest)

        return max_interest

    def get_current_interest(self, payload: dict) -> int:
        '''
        Gets the current interest for a given keyword.

        :param payload: Dict with timeline data including interest.
        '''
        interest_over_time = payload.get('interest_over_time', [])
        if not interest_over_time:
            logger.warning('Could not extract interest over time data.')
            return -1

        timeline_data = interest_over_time.get('timeline_data', []) 
        if not timeline_data:
            logger.warning('Could not extract timeline data.')
            return -1
        
        query = payload.get('search_parameters').get("q")

        if query:
            multiple_queries = query.split(",")

        for entry in timeline_data:
            date = entry.get('date')

            if not date:
                continue

            current_date = datetime.now()
            current_date = current_date.date()

            start_date, end_date = self.get_date_interval(date)

            values = []
            if current_date >= start_date and current_date <= end_date:
                values = entry.get('values')

                if not values:
                    logger.error('Could not extract information for keyword.')
                    return -1

            for value_entry in values:
                if value_entry.get('query') in multiple_queries:
                    return value_entry.get('extracted_value', -1)

        logger.error('Could not find current date.')
        return -1


    def get_date_interval(self, date_string: str) -> tuple[date, date]:
        '''
        Gets the time interval for a given date string.

        :param date_string: String with the format "%b %d - %b %d, %Y"
        '''
        if "–" in date_string and date_string.count(",") == 2:
            start_str, end_str = [part.strip() for part in date_string.split("–")]
            start_date = datetime.strptime(start_str, "%b %d, %Y").date()
            end_date = datetime.strptime(end_str, "%b %d, %Y").date()
            return start_date, end_date

        # Split into parts
        date_range, year = date_string.rsplit(",", 1)
        start_str, end_str = date_range.split("–")

        start_str = start_str.strip()
        end_str = end_str.strip()
        year = year.strip()

        start_parts = start_str.split(" ")
        if len(start_parts) == 2:
            start_month, start_day = start_parts
        else:
            raise ValueError(f"Unexpected start date format: {start_str}")

        if len(end_str.split(" ")) == 1:
            end_str = f"{start_month} {end_str}"

        # Parse start and end dates
        start_date = datetime.strptime(f"{start_str} {year}", "%b %d %Y").date()
        end_date = datetime.strptime(f"{end_str} {year}", "%b %d %Y").date()

        return (start_date, end_date)

    def get_start_end_date(self, payload: dict) -> tuple[date, date]:
        '''
        Gets the start and end date for the timeline data.

        :param paylaod: dict object containing keywords information.
        '''

        interest_over_time = payload.get('interest_over_time', [])
        if not interest_over_time:
            raise KeyError('Failed to get interest over time.')
        
        timeline_data = interest_over_time.get('timeline_data', [])
        if not timeline_data:
            raise KeyError('Failed to get timeline data.')

        min_date, max_date = None, None
        for entry in timeline_data:
            start, end = self.get_date_interval(entry.get('date'))
            if not min_date or start < min_date:
                min_date = start
            
            if not max_date or end> max_date:
                max_date = end
            
        return (min_date, max_date)

