import logging
from typing import List
from uuid import uuid4

from pydantic import parse_obj_as
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256

from src.model import APIClient


logger = logging.getLogger('beamline_service.api_auth')


class AuthService():
    '''
    Access and management of API clients
    '''

    def __init__(self, client, db_name=None):
        '''
        Initializes AuthService
        Args:
            client:     Mongo client
            db_name:    Database name
        '''
        if db_name is None:
            db_name = 'api_auth'
        self._db = client[db_name]
        self._collection_api_client = self._db.api_client
        pass

    def create_api_client(self, submitter: str, client: str, api: str) -> str:
        '''
        Create API client
        Args:
            client:     APIClient
            api:        api associated with client
        Returns:
            client_key
        '''
        try:
            key = str(uuid4())
            hashed_key = pbkdf2_sha256.hash(key)
            client_key = APIClient(hashed_key=hashed_key, client=client, api=api)
            self._collection_api_client.insert_one(client_key.dict())
            return key
        except Exception as e:
            logging.error(e)
            raise e

    def verify_api_key(self, key):
        '''
        Verify the API key
        Args:
            key:        string with api key
        Returns:
            api_client if verified, ow None
        '''
        for api_client in self.get_api_clients(
            "sys"
        ):
            if pbkdf2_sha256.verify(key, api_client.hashed_key):
                return api_client
        return None

    def get_api_clients(self, submitter: str) -> List[APIClient]:
        '''
        Retrieve the list of API clients
        Returns:
            List of APIClients
        '''
        try:
            keys = list(self._collection_api_client.find())
            return parse_obj_as(List[APIClient], keys)
        except Exception as e:
            logging.error(e)
            raise e

