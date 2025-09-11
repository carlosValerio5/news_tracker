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
