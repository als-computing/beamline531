from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Extra, Field
from typing import Dict, List, Optional


SCHEMA_VERSION = "0.1"
DEFAULT_UID = "342e4568-e23b-12d3-a456-526714178000"
DEFAULT_TIME = datetime.utcnow()


## Auth-related classes

class APIClient(BaseModel):
    hashed_key: str = Field(description="API key that can be given to a client")
    client: str = Field(description="Name of client who key is given to")
    api: str = Field(description="Name of API that key gives access to")


## Beamline-related classes

class DeviceType(str, Enum):
    control = "ophyd.EpicsMotor"
    signal = "ophyd.EpicsSignal"
    detector = "ophyd.AreaDetector"


class BeamlineComponent(BaseModel):
    schema_version: str = SCHEMA_VERSION
    uid: str = DEFAULT_UID
    name: str = Field(description="epics name")
    prefix: str = Field(description="epics prefix")
    active: bool = Field(description="the component is active")
    device_class: DeviceType
    documentation: Optional[str]
    kwargs: Optional[Dict]
    creation: datetime = DEFAULT_TIME
    last_edit: datetime = DEFAULT_TIME
    unit: Optional[str] = Field(description="unit")
    z: Optional[float] = Field(description="")
    port: Optional[str] = Field(description="port connection")


class Beamline(BaseModel):
    schema_version: str = SCHEMA_VERSION
    uid: str = DEFAULT_UID
    name: str = Field(description="beamline name")
    creation: datetime = DEFAULT_TIME
    last_edit: datetime = DEFAULT_TIME
    components: Optional[List[BeamlineComponent]] = []
    class Config:
        extra = Extra.ignore


class BeamlinePatchRequest(BaseModel):
    add_components: Optional[List[BeamlineComponent]]
    remove_components: Optional[List[str]]
    modify_components: Optional[List[BeamlineComponent]]
