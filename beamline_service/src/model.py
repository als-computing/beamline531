from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Extra, Field
from typing import Any, Dict, List, Optional, Union

SCHEMA_VERSION = "0.0"
DEFAULT_UID = "342e4568-e23b-12d3-a456-526714178000"
DEFAULT_UID_LIST = [DEFAULT_UID]


class ComponentType(str, Enum):
    control = "control"
    detector = "detector"


class BasicComponent(BaseModel):
    schema_version: int = 1                         # data schema version
    uid: str = DEFAULT_UID
    id: str = Field(description="base id for dash GUI components")
    type: ComponentType
    name: str = Field(description="epics name")
    prefix: str = Field(description="epics prefix")
    timeout: Optional[float] = 2.0
    units: str = Field(description="units")
    min: Optional[float] = Field(description="minimum position")
    max: Optional[float] = Field(description="maximum position")
    step: Optional[float] = Field(description="step size")
    settle_time: Optional[float] = Field(description="amount of time to wait after moves to report status completion")
    gui_comp: Optional[List] = []                   # GUI component
    comp: Optional[Any] = None                      # ophyd object
    status: str = 'Online'


class Beamline(BaseModel):
    uid: str = DEFAULT_UID
    schema_version: str = SCHEMA_VERSION
    version: int
    name: str
    components_uids: List[str] = DEFAULT_UID_LIST
    class Config:
        extra = Extra.ignore


class ClientBeamline(Beamline):
    Components: List[BasicComponent] = []
