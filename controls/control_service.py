from pymongo.mongo_client import MongoClient
import uuid
from typing import Iterator, List, Tuple
from uuid import uuid4

from model import Beamline, FullBeamline, Control


class BeamlineNotFound(Exception):
    pass


class ControlNotFound(Exception):
    pass


class ControlService():
    """
    """

    def __init__(self, client, db_name=None):
        """
        """
        if db_name is None:
            db_name = 'control'
        self._db = client[db_name]
        self._collection_beamline = self._db.beamline
        self._collection_beamline_revision = self._db.beamline_revision
        self._collection_control = self._db.control
        self._collection_control_revision = self._db.control_revision
        self._create_indexes()

    def create_control(self, control: Control) -> str:
        control.uid = str(uuid4())
        self._collection_control.insert_one(control.dict())
        return control.uid
    
    def create_beamline(self, beamline: Beamline) -> str:
        beamline.uid = str(uuid4())
        self._collection_beamline.insert_one(beamline.dict())
        return beamline.uid
    
    def get_control(self, uid: str) -> Control:
        item = self._collection_control.find_one({'uid': uid})
        if not item:
            raise ControlNotFound(f'no control with id: {uid}')
        self._clean_id(item)
        control = Control.parse_obj(item)
        return control
    
    def get_beamline(self, uid: str) -> FullBeamline:
        item = self._collection_beamline.find_one({'uid': uid})
        if not item:
            raise BeamlineNotFound(f'no beamline with id: {uid}')
        self._clean_id(item)
        beamline = Beamline.parse_obj(item)
        controls = []
        for control_uid in beamline.controls_uids:
            controls.append(self.get_control(control_uid))
        full_beamline = FullBeamline.parse_obj(beamline)
        full_beamline.controls = controls
        return full_beamline
    
    def _create_indexes(self):
        self._collection_beamline.create_index([('uid', 1)], unique=True)
        self._collection_control.create_index([('uid', 1)], unique=True)
    
    @staticmethod
    def _clean_id(data):
        """
        Removes the mongo ID
        """
        if '_id' in data:
            del data['_id']


class Context:
    db: MongoClient = None
    control_svc: ControlService = None


context = Context