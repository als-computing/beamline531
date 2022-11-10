import logging
from typing import List, Optional

from fastapi import FastAPI, Query as FastQuery, HTTPException
from pydantic import BaseModel
from starlette.config import Config

from model import FullBeamline, Beamline, Control
from control_service import ControlService, Context

logger = logging.getLogger('control_api')

DEFAULT_PAGE_SIZE = 20


def init_logging():
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(CONTROL_LOG_LEVEL)


config = Config(".env")
MONGO_DB_URI = config("MONGO_DB_URI", cast=str, default="mongodb://localhost:27017/control")
CONTROL_DB_NAME = config("CONTROL_DB_NAME", cast=str, default="control")
CONTROL_LOG_LEVEL = config("CONTROL_LOG_LEVEL", cast=str, default="INFO")

API_URL_PREFIX = "/api/v0"

init_logging()

app = FastAPI(
    openapi_url="/api/beamline_control/openapi.json",
    docs_url="/api/beamline_control/docs",
    redoc_url="/api/beamline_control/redoc")

svc_context = Context

@app.on_event("startup")
async def startup_event():
    from pymongo import MongoClient
    logger.debug('!!!!!!!!!starting server')
    db = MongoClient(MONGO_DB_URI)
    set_control_service(ControlService(db))


def set_control_service(new_control_svc: ControlService):
    global control_svc
    control_svc = new_control_svc


class CreateResponseModel(BaseModel):
    uid: str


@app.post(API_URL_PREFIX + '/controls', tags=['controls'], response_model=CreateResponseModel)
def add_control(control: Control):
    new_control_uid = control_svc.create_control(control)
    return CreateResponseModel(uid=new_control_uid)


@app.get(API_URL_PREFIX + '/control/{uid}', tags=['controls'], response_model=Control)
def get_beamline(uid: str) -> Control:
    control = control_svc.get_control(uid)
    return control


@app.post(API_URL_PREFIX + '/beamlines', tags=['beamlines'], response_model=CreateResponseModel)
def add_beamline(beamline: Beamline):
    new_beamline_uid = control_svc.create_beamline(beamline)
    return CreateResponseModel(uid=new_beamline_uid)


@app.get(API_URL_PREFIX + '/beamline/{uid}', tags=['beamlines'], response_model=FullBeamline)
def get_beamline(uid: str) -> FullBeamline:
    beamline = control_svc.get_beamline(uid)
    return beamline


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)