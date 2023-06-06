import logging, os
from typing import List, Optional

from fastapi import Security, FastAPI, Depends, HTTPException, Query as FastQuery
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from pydantic import BaseModel
from pymongo import MongoClient
from starlette.status import HTTP_403_FORBIDDEN
import uvicorn

from src.beamline_service import BeamlineService
from src.api_auth_service import AuthService
from src.model import Beamline, BeamlinePatchRequest, BeamlineComponent


logger = logging.getLogger('beamline_service.api')


def init_logging():
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(COMP_LOG_LEVEL)


MONGO_DB_USERNAME = str(os.environ.get('MONGO_INITDB_ROOT_USERNAME', default=""))
MONGO_DB_PASSWORD = str(os.environ.get('MONGO_INITDB_ROOT_PASSWORD', default=""))
MONGO_DB_URI = "mongodb://%s:%s@mongodb_bl531:27017/?authSource=admin" % (MONGO_DB_USERNAME, MONGO_DB_PASSWORD)
MONGO_DB_NAME = "beamline"
COMP_LOG_LEVEL = "INFO"
API_URL_PREFIX = "/api/v0"
API_KEY_NAME = "api_key"
BEAMLINE_API = "beamline_api"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


init_logging()


app = FastAPI(
    openapi_url="/api/beamline_component/openapi.json",
    docs_url="/api/beamline_component/docs",
    redoc_url="/api/beamline_component/redoc")


@app.on_event("startup")
async def startup_event():
    logger.info('starting beamline api server')
    db = MongoClient(MONGO_DB_URI)[MONGO_DB_NAME]
    set_beamline_service(BeamlineService(db))
    set_auth_service(AuthService(db))


async def get_api_key_from_request(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_query:
        return api_key_query
    elif api_key_header:
        return api_key_header
    elif api_key_cookie:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Could not validate credentials"
        )


def set_beamline_service(new_beamline_svc: BeamlineService):
    global beamline_svc
    beamline_svc = new_beamline_svc


def set_auth_service(new_auth_svc: AuthService):
    global auth_svc
    auth_svc = new_auth_svc


class CreatePatchResponseModel(BaseModel):
    added_uids: Optional[List[str]]
    removed_uids: Optional[List[str]]


class CreateResponseModel(BaseModel):
    uid: str


@app.post(
        API_URL_PREFIX + '/beamline', 
        tags=['beamline'], 
        response_model=CreateResponseModel
    )
async def add_beamline(
    beamline: Beamline, 
    api_key: APIKey = Depends(get_api_key_from_request)
) -> CreateResponseModel:
    client_key: APIKey = auth_svc.verify_api_key(api_key)
    if not client_key:
        logger.info("forbidden  {api_key}")
        raise HTTPException(status_code=403)
    new_beamline_uid = beamline_svc.create_beamline(beamline)
    return CreateResponseModel(uid=new_beamline_uid)


@app.patch(
        API_URL_PREFIX + '/beamline/{uid}', 
        tags=['beamline'], 
        response_model=CreatePatchResponseModel
    )
async def modify_beamline_components(
    uid: str, 
    req: BeamlinePatchRequest, 
    api_key: APIKey = Depends(get_api_key_from_request)
) -> CreatePatchResponseModel:
    client_key: APIKey = auth_svc.verify_api_key(api_key)
    if not client_key:
        logger.info("forbidden  {api_key}")
        raise HTTPException(status_code=403)
    added_uids, removed_uids = beamline_svc.modify_beamline_components(uid, req)
    return CreatePatchResponseModel(added_uids=added_uids, removed_uids=removed_uids)


@app.get(
        API_URL_PREFIX + '/beamlines', 
        tags=['beamline'], 
        response_model=List[Beamline]
    )
async def get_beamlines(
    names: Optional[List[str]]=FastQuery(None), 
    api_key: APIKey = Depends(get_api_key_from_request)
) -> List[Beamline]:
    client_key: APIKey = auth_svc.verify_api_key(api_key)
    if not client_key:
        logger.info("forbidden  {api_key}")
        raise HTTPException(status_code=403)
    beamlines = beamline_svc.get_beamlines(names)
    return beamlines


@app.get(
        API_URL_PREFIX + '/beamline/{uid}', 
        tags=['beamline'], 
        response_model=Beamline
        )
async def get_beamline(
    uid: str, 
    api_key: APIKey = Depends(get_api_key_from_request)
) -> Beamline:
    client_key: APIKey = auth_svc.verify_api_key(api_key)
    if not client_key:
        logger.info("forbidden  {api_key}")
        raise HTTPException(status_code=403)
    beamline = beamline_svc.get_beamline(uid)
    return beamline


@app.get(
        API_URL_PREFIX + '/beamline/{uid}/components', 
        tags=['beamline'], 
        response_model=List[BeamlineComponent]
        )
async def get_beamline_components(
    uid: str, 
    api_key: APIKey = Depends(get_api_key_from_request)
) -> List[BeamlineComponent]:
    client_key: APIKey = auth_svc.verify_api_key(api_key)
    if not client_key:
        logger.info("forbidden  {api_key}")
        raise HTTPException(status_code=403)
    beamline_components = beamline_svc.get_components(uid)
    return beamline_components


@app.delete(
        API_URL_PREFIX + '/beamline/{uid}', 
        tags=['beamline'], 
        response_model=Beamline
        )
async def delete_beamline(
    uid: str, 
    api_key: APIKey = Depends(get_api_key_from_request)
) -> str:
    client_key: APIKey = auth_svc.verify_api_key(api_key)
    if not client_key:
        logger.info("forbidden  {api_key}")
        raise HTTPException(status_code=403)
    beamline_uid = beamline_svc.delete_beamline(uid)
    return CreateResponseModel(uid=beamline_uid)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8090)