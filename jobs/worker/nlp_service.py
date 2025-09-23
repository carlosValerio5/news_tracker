import spacy

class HeadlineProcessService:
    '''Handles bussiness logic for natural language processing'''

    POS_WEIGHTS = {
        "PROPN": 2.0,
        "NOUN": 1.5,
        "ADJ": 1.0
    }

    LABEL_WEIGHTS = {
        "PERSON": 2.0,
        "GPE": 1.5,
        "ORG": 1.0
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
            'extraction_confidence' : extraction_confidence 
        }

        if not article_keyword.get('keyword_1'):
            raise ValueError(f'Unable to extract keyword_1, from {headline}')
        
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
                    confidence = self.get_level_of_confidence(token.pos_, idx)
                    keywords.append((kw, confidence))
                
        keywords.sort(key=lambda x: x[1], reverse=True)

        return [(kw.capitalize(), score) for kw, score in keywords[:max_keywords]]

    def get_principal_keyword(self, preprocessed_keywords: list) -> list:
        '''
        Returns a single keyword, representing the most important keyword from a set of keywords

        :param preprocessed_keywords: List of keywords to process. 
        '''
        if not preprocessed_keywords:
            raise ValueError("preprocessed_keywords required.")

        keyword_string = ' '.join(preprocessed_keywords).strip()
        doc = self._nlp(keyword_string)
        
        if not doc:
            raise Exception('Failed to process keywords list.')

        max_score = -1
        keyword = str()
        for idx, ent in enumerate(doc.ents, start=1):
            if ent.label_ in self.LABEL_WEIGHTS.keys():

                label_score = self.LABEL_WEIGHTS[ent.label_]
                position_score = 1/idx # earlier keywords get higher scores
                score = label_score + position_score

                if score > max_score:
                    max_score = score
                    keyword = ent.text

        if not keyword and preprocessed_keywords:
            keyword = preprocessed_keywords[0]
            
        return keyword
