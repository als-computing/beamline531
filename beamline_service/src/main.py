import logging, os
from typing import List, Optional

from fastapi import FastAPI, Query as FastQuery, HTTPException
from pydantic import BaseModel
from starlette.config import Config
import uvicorn

from model import ClientBeamline, Beamline, BasicComponent
from component_service import ComponentService, Context

logger = logging.getLogger('component_api')

DEFAULT_PAGE_SIZE = 20
MONGO_DB_USERNAME = str(os.environ['MONGO_INITDB_ROOT_USERNAME'])
MONGO_DB_PASSWORD = str(os.environ['MONGO_INITDB_ROOT_PASSWORD'])

def init_logging():
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(COMP_LOG_LEVEL)


config = Config(".env")
MONGO_DB_URI = "mongodb://%s:%s@mongodb_bl531:27017/?authSource=admin" % (MONGO_DB_USERNAME, MONGO_DB_PASSWORD)
COMP_DB_NAME = config("COMP_DB_NAME", cast=str, default="component")
COMP_LOG_LEVEL = config("COMP_LOG_LEVEL", cast=str, default="INFO")

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
    set_component_service(ComponentService(db))


def set_component_service(new_component_svc: ComponentService):
    global component_svc
    component_svc = new_component_svc


class CreateComponentsResponseModel(BaseModel):
    uids: List[str]


class CreateResponseModel(BaseModel):
    uid: str


@app.post(API_URL_PREFIX + '/components', tags=['components'], response_model=CreateComponentsResponseModel)
def add_components(components: List[BasicComponent]):
    new_components_uids = component_svc.create_components(components)
    return CreateComponentsResponseModel(uids=new_components_uids)


@app.get(API_URL_PREFIX + '/component/{uid}', tags=['components'], response_model=BasicComponent)
def get_component(uid: str) -> BasicComponent:
    component = component_svc.get_component(uid)
    return component


@app.post(API_URL_PREFIX + '/beamlines', tags=['beamlines'], response_model=CreateResponseModel)
def add_beamline(beamline: Beamline):
    new_beamline_uid = component_svc.create_beamline(beamline)
    return CreateResponseModel(uid=new_beamline_uid)


@app.get(API_URL_PREFIX + '/beamline/{uid}', tags=['beamlines'], response_model=ClientBeamline)
def get_beamline(uid: str) -> ClientBeamline:
    beamline = component_svc.get_beamline(uid)
    return beamline


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8090)