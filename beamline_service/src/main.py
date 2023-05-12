import logging, os
from typing import List, Optional

from pydantic import BaseModel
from starlette.config import Config
import uvicorn

from fastapi import FastAPI, Query as FastQuery
from model import Beamline, BeamlinePatchRequest, Scan
from beamline_service import BeamlineService, Context

logger = logging.getLogger('beamline_api')

def init_logging():
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(COMP_LOG_LEVEL)


MONGO_DB_USERNAME = str(os.environ.get('MONGO_INITDB_ROOT_USERNAME', default=""))
MONGO_DB_PASSWORD = str(os.environ.get('MONGO_INITDB_ROOT_PASSWORD', default=""))
MONGO_DB_URI = "mongodb://%s:%s@mongodb_bl531:27017/?authSource=admin" % (MONGO_DB_USERNAME, MONGO_DB_PASSWORD)
COMP_DB_NAME = "beamline"
COMP_LOG_LEVEL = "INFO"

API_URL_PREFIX = "/api/v0"

init_logging()

app = FastAPI(
    openapi_url="/api/beamline_component/openapi.json",
    docs_url="/api/beamline_component/docs",
    redoc_url="/api/beamline_component/redoc")

svc_context = Context

@app.on_event("startup")
async def startup_event():
    from pymongo import MongoClient
    logger.debug('!!!!!!!!!starting server')
    db = MongoClient(MONGO_DB_URI)
    set_beamline_service(BeamlineService(db))


def set_beamline_service(new_beamline_svc: BeamlineService):
    global beamline_svc
    beamline_svc = new_beamline_svc


class CreatePatchResponseModel(BaseModel):
    added_uids: Optional[List[str]]
    removed_uids: Optional[List[str]]


class CreateResponseModel(BaseModel):
    uid: str


@app.post(API_URL_PREFIX + '/beamline', tags=['beamline'], response_model=CreateResponseModel)
def add_beamline(beamline: Beamline) -> CreateResponseModel:
    new_beamline_uid = beamline_svc.create_beamline(beamline)
    return CreateResponseModel(uid=new_beamline_uid)


@app.patch(API_URL_PREFIX + '/beamline/{uid}', tags=['beamline'], response_model=CreatePatchResponseModel)
def modify_beamline_components(uid: str, req: BeamlinePatchRequest) -> CreatePatchResponseModel:
    added_uids, removed_uids = beamline_svc.modify_beamline_components(uid, req)
    return CreatePatchResponseModel(added_uids=added_uids, removed_uids=removed_uids)


@app.get(API_URL_PREFIX + '/beamlines', tags=['beamline'], response_model=List[Beamline])
def get_beamlines(names: Optional[List[str]]=FastQuery(None)) -> List[Beamline]:
    beamlines = beamline_svc.get_beamlines(names)
    return beamlines


@app.get(API_URL_PREFIX + '/beamline/{uid}', tags=['beamline'], response_model=Beamline)
def get_beamline(uid: str) -> Beamline:
    beamline = beamline_svc.get_beamline(uid)
    return beamline


@app.delete(API_URL_PREFIX + '/beamline/{uid}', tags=['beamline'], response_model=Beamline)
def delete_beamline(uid: str) -> str:
    beamline_uid = beamline_svc.delete_beamline(uid)
    return CreateResponseModel(uid=beamline_uid)


# @app.post(API_URL_PREFIX + 'beamline/{uid}/qserver/status', tags=['qserver'], response_model=str)
# def qserver_status(uid: str) -> str:
#     response = beamline_svc.get_qserver_status(uid)
#     return response


# @app.post(API_URL_PREFIX + 'beamline/{uid}/qserver/open', tags=['qserver'], response_model=str)
# def qserver_open(uid: str) -> str:
#     response = beamline_svc.open_qserver_env(uid)
#     return response


# @app.post(API_URL_PREFIX + 'beamline/{uid}/qserver/close', tags=['qserver'], response_model=str)
# def qserver_close(uid: str) -> str:
#     response = beamline_svc.close_qserver_env(uid)
#     return response


# @app.post(API_URL_PREFIX + 'beamline/{uid}/add_scan', tags=['scan'], response_model=str)
# def add_scan(uid: str, scan: Scan) -> str:
#     response = beamline_svc.add_scan(uid, scan)
#     return response


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8090)