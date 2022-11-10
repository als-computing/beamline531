from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Extra
from typing import Any, Dict, List, Optional, Union

SCHEMA_VERSION = "0.0"
DEFAULT_UID = "342e4568-e23b-12d3-a456-526714178000"
DEFAULT_UID_LIST = [DEFAULT_UID]


class SimpleComponent(BaseModel):
    name: str
    title: str
    param_key: str
    value: Optional[int]


class Slider(SimpleComponent):
    comp_type: str = 'slider'
    value_min: Optional[int]
    value_max: Optional[int]


class Radio(SimpleComponent):
    comp_type: str = 'radio'
    options: List


class Control(BaseModel):
    uid: str = DEFAULT_UID
    pv_name: str
    name: str
    gui_comp: List[Union[Slider, Radio]]


class Beamline(BaseModel):
    uid: str = DEFAULT_UID
    schema_version: str = SCHEMA_VERSION
    version: int
    name: str
    controls_uids: List[str] = DEFAULT_UID_LIST
    class Config:
        extra = Extra.ignore


class FullBeamline(Beamline):
    controls: List[Control] = []
