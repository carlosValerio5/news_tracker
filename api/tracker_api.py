from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def health_check():
    '''Checks health api, sqs and db connections.'''
    return {"Status": "Running"}

@app.get('/headlines')
def get_headlines():
    '''Gets news headlines.'''
    pass

@app.get('/keywords')
def get_keywords(): # use nlp service or get from db, if from db keywords max = 3
    '''
    Gets headlines keywords

    :param keyword_number: Specifies the number of keywords to get.
    '''

@app.get('/keywords/{id}')
def get_keyword_by_id(keywords_id: int):
    '''
    Gets specific keyword set by id

    :param keywords_id: Unique id for keywords.
    '''
    pass
