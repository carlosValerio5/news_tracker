from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req_lib
from logger.logging_config import logger


class SecurityService:

    @staticmethod
    def exchange_code_for_tokens(code:str, client_id:str, client_secret:str, redirect_uri:str):
        '''
        Exchanges the authorization code for access and ID tokens.

        :param code: Authorization code received from Google.
        :param client_id: Google OAuth2 client ID.
        :param client_secret: Google OAuth2 client secret.
        :param redirect_uri: Redirect URI used in the OAuth2 flow.
        '''
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = req_lib.post(token_url, data=payload)
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange code for tokens."
            )
        return response.json()

    @staticmethod
    def verify_id_token(id_token_str: str, client_id: str):
        '''
        Verifies the ID token and returns the token's payload.

        :param id_token_str: ID token string to verify.
        :param client_id: Google OAuth2 client ID.
        '''
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                audience=client_id,
                clock_skew_in_seconds=10
                )
            return idinfo
        except ValueError as e:
            logger.error(f"Failed to verify ID token: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid ID token."
            )
