from pymongo.mongo_client import MongoClient
import uuid
from typing import Iterator, List, Tuple
from uuid import uuid4

from model import Beamline, ClientBeamline, BasicComponent


class BeamlineNotFound(Exception):
    pass


class ComponentNotFound(Exception):
    pass


class ComponentService():
    """
    """

    def __init__(self, client, db_name=None):
        """
        """
        if db_name is None:
            db_name = 'beamline_components'
        self._db = client[db_name]
        self._collection_beamline = self._db.beamline
        self._collection_beamline_revision = self._db.beamline_revision
        self._collection_component = self._db.component
        self._create_indexes()

    def create_components(self, components: List[BasicComponent]) -> List[str]:
        component_uids = []
        for component in components:
            component.uid = str(uuid4())
            self._collection_component.insert_one(component.dict())
            component_uids.append(component.uid)
        return component_uids
    
    def create_beamline(self, beamline: Beamline) -> str:
        beamline.uid = str(uuid4())
        self._collection_beamline.insert_one(beamline.dict())
        return beamline.uid
    
    def get_component(self, uid: str) -> BasicComponent:
        item = self._collection_component.find_one({'uid': uid})
        if not item:
            raise ComponentNotFound(f'no component with id: {uid}')
        self._clean_id(item)
        component = BasicComponent.parse_obj(item)
        return component
    
    def get_beamline(self, uid: str) -> ClientBeamline:
        item = self._collection_beamline.find_one({'uid': uid})
        if not item:
            raise BeamlineNotFound(f'no beamline with id: {uid}')
        self._clean_id(item)
        beamline = Beamline.parse_obj(item)
        components = []
        for component_uid in beamline.components_uids:
            components.append(self.get_component(component_uid))
        client_beamline = ClientBeamline.parse_obj(beamline)
        client_beamline.Components = components
        return client_beamline
    
    def _create_indexes(self):
        self._collection_beamline.create_index([('uid', 1)], unique=True)
        self._collection_component.create_index([('uid', 1)], unique=True)
    
    @staticmethod
    def _clean_id(data):
        """
        Removes the mongo ID
        """
        if '_id' in data:
            del data['_id']


class Context:
    db: MongoClient = None
    component_svc: ComponentService = None


context = Context