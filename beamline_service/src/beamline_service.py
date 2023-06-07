from datetime import datetime
from pymongo.mongo_client import MongoClient
from typing import Iterator, List
from uuid import uuid4

from src.model import Beamline, BeamlinePatchRequest, BeamlineComponent


class BeamlineNotFound(Exception):
    pass


class BeamlineService():
    '''
    Access and management of the Beamline database
    '''

    def __init__(self, client, db_name=None):
        '''
        Initializes BeamlineService
        Args:
            client:     Mongo client
            db_name:    Database name
        '''
        if db_name is None:
            db_name = 'beamline_components'
        self._db = client[db_name]
        self._collection_beamline = self._db.beamline
        self._create_indexes()
        pass
    
    def create_beamline(self, beamline: Beamline) -> str:
        '''
        Creates a beamline entry in the database
        Args:
            beamline:   Beamline details
        Returns:
            breamline uid
        '''
        beamline.uid = str(uuid4())     # Assign uuid to beamline
        current_time = datetime.utcnow()
        beamline.creation = current_time
        beamline.last_edit = current_time
        for cont in range(len(beamline.components)):
            beamline.components[cont].uid = str(uuid4())
            beamline.components[cont].creation = current_time
            beamline.components[cont].last_edit = current_time
        self._collection_beamline.insert_one(beamline.dict())
        return beamline.uid
    
    def get_beamline(self, uid: str) -> Beamline:
        '''
        Retrieves a beamline from the database
        Args:
            uid:        Beamline uid
        Returns:
            beamline:   Beamline object with the details of the beamline
        '''
        item = self._collection_beamline.find_one({'uid': uid})
        if not item:
            raise BeamlineNotFound(f'no beamline with id: {uid}')
        self._clean_id(item)
        beamline = Beamline.parse_obj(item)
        return beamline
    
    def get_components(self, uid: str) -> List[BeamlineComponent]:
        '''
        Retrieves all the components of a beamline from the database
        Args:
            uid:            Beamline uid
        Returns:
            components:     List of beamline components
        '''
        beamline = self.get_beamline(uid)
        return beamline.components
    
    def get_beamlines(self, names: List[str]=None) -> Iterator[Beamline]:
        '''
        Retrieves a beamline from the database
        Args:
            names:      Beamline names
        Returns:
            beamline:   Beamline object with the details of the beamline
        '''
        query = {}
        if names:
            query = {'name': {'$in': names}}
        items = self._collection_beamline.find(query)
        if not items:
            raise BeamlineNotFound(f'no beamline with names: {names}')
        for item in items:
            self._clean_id(item)
            yield Beamline.parse_obj(item)
    
    def delete_beamline(self, uid: str) -> str:
        '''
        Deletes a beamline from the database
        Args:
            uid:        Beamline uid to be deleted
        Returns:
            uid of the removed beamline
        '''
        item = self._collection_beamline.find_one({'uid': uid})
        if not item:
            raise BeamlineNotFound(f'no beamline with id: {uid}')
        self._collection_beamline.delete_one({'uid': uid})
        return uid

    
    def modify_beamline_components(self, beamline_uid: str, req: BeamlinePatchRequest) -> str:
        '''
        Modifies the components of a beamline
        Args:
            beamline_uid:   Beamline to be modified
            req:            Requirement details (components to add and/or components to delete)
        Returns:
            added_components_uid
            removed_components_uid
        '''
        added_components_uid = []
        removed_components_uid = []
        modify_components_uid = []
        # get beamline
        beamline = self.get_beamline(uid= beamline_uid)
        # add beamline components
        add_components = req.add_components
        if add_components:
            components_dict = []
            for component in add_components:
                component.uid = str(uuid4())
                current_time = datetime.utcnow()
                component.creation = current_time
                component.last_edit = current_time
                added_components_uid.append(component.uid)
                components_dict.append(component.dict())
            current_time = datetime.utcnow()
            self._collection_beamline.update_one({"uid": beamline_uid}, {"$push": {"components": {"$each":  components_dict}}, \
                                                                         "$set": {"last_edit": current_time}})
        # remove beamline components
        remove_components = req.remove_components
        if remove_components:
            if beamline.components == []:
                removed_components_uid = ['-1'] * len(remove_components)
            current_time = datetime.utcnow()
            result = self._collection_beamline.update_one({"uid": beamline_uid}, \
                                                          {"$pull": {"components": {"uid": {"$in": remove_components}}}, \
                                                           "$set": {"last_edit": current_time}})
            removed_components_uid = remove_components
            # if the number of deleted elements does not match the number of components,
            # finds the component UIDs that were not deleted
            if result.modified_count is not len(remove_components):
                current_components_uid = [component.uid for component in beamline.components]
                for cont, component_uid in enumerate(removed_components_uid):
                    if component_uid not in current_components_uid:
                        removed_components_uid[cont] = -1
        modify_components = req.modify_components
        if modify_components:
            for comp in modify_components:
                comp_uid = comp.uid
                current_time = datetime.utcnow()
                comp.last_edit = current_time
                comp_dict = comp.dict()
                result = self._collection_beamline.update_one({"uid": beamline_uid, "components.uid": comp_uid}, \
                                                              {"$set": {"components.$" : comp_dict , "last_edit": current_time}})
                modify_components_uid.append(comp_uid)
        return added_components_uid, removed_components_uid, modify_components_uid
    
    def _create_indexes(self):
        self._collection_beamline.create_index([('uid', 1)], unique=True)
        self._collection_beamline.create_index([('id', 1)], unique=True)
        self._collection_beamline.create_index([('components.uid', 1)], unique=True)
    
    @staticmethod
    def _clean_id(data):
        """
        Removes the mongo ID
        """
        if '_id' in data:
            del data['_id']
