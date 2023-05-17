from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Extra, Field
from typing import Dict, List, Optional


SCHEMA_VERSION = "0.1"
DEFAULT_UID = "342e4568-e23b-12d3-a456-526714178000"
DEFAULT_TIME = datetime.utcnow()


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


class QueueServer(BaseModel):
    url: str = Field(description="Queue-server URL")
    api_key: str = Field(description="API key to server")


class Beamline(BaseModel):
    schema_version: str = SCHEMA_VERSION
    uid: str = DEFAULT_UID
    name: str = Field(description="beamline name")
    creation: datetime = DEFAULT_TIME
    last_edit: datetime = DEFAULT_TIME
    qserver: QueueServer
    components: Optional[List[BeamlineComponent]] = []
    class Config:
        extra = Extra.ignore


class BeamlinePatchRequest(BaseModel):
    add_components: Optional[List[BeamlineComponent]]
    remove_components: Optional[List[str]]


class Scan(BaseModel):
    name: str = Field(description="name for scan")
    detectors: List = Field(description="list of detectors")
    controls: str = Field(description="control to move")
    start: float = Field(description="start position for scan")
    stop: float = Field(description="stop position for scan")
    num_step: int = Field(description="number of steps for scan")
