import os
from pymongo import MongoClient

from src.api_auth_service import AuthService
from src.main import MONGO_DB_NAME, MONGO_DB_URI, BEAMLINE_API

db = MongoClient(MONGO_DB_URI)[MONGO_DB_NAME]

auth_svc = AuthService(db)

key = auth_svc.create_api_client("submitter", "bl531", BEAMLINE_API)
print(f"create key {key} for api {BEAMLINE_API}")