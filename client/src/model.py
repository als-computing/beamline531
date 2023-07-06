import logging
from enum import Enum

from pydantic import BaseModel
import requests
from typing import Optional, List, Any

from src.epics_db.ophyd_dash import OphydDash


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class ComponentType(str, Enum):
    control = "control"
    detector = "detector"


class BeamlineComponents():
    def __init__(self, components: List[OphydDash]):
        self.comp_list = components
        self.comp_id_list = [c.id for c in components]

    def get_gui(self):
        '''
        Retrieves the GUI components
        '''
        gui_comp_list = []
        for component in self.comp_list:
            if component.gui_comp is not None:
                gui_comp_list = gui_comp_list + component.gui_comp
        return gui_comp_list
    
    def find_component(self, base_id:'str'=None):
        '''
        Searches for the corresponding component within the component list based on the 
        value of base_id. If no component is found, returns None
        '''
        try:
            idx = self.comp_id_list.index(base_id)
            return self.comp_list[idx]
        except ValueError as e:
            logging.error(f'Base id {base_id} was not found among the list of components.')
            return None
    
    def find_comp_type(self, comp_type):
        '''
        Filters the list of components based on a component type
        '''
        list_comp_type = []
        for component in self.comp_list:
            if component.type == ComponentType(comp_type):
                list_comp_type.append(component)
        return list_comp_type


class QServer(BaseModel):
    api_url: str
    api_key: str

    def get_status(self):
        '''
        Retrieves the current status of QServer
        '''
        response = requests.post(f'{self.api_url}/status', headers={'Authorization': f'ApiKey {self.api_key}'})
        if response.status_code != 200:
            logging.error(f'Could not retrieve status {response.status_code}:{response.json()}')
        return response.json()

    def open_env(self):
        '''
        Opens a new environment in QServer
        '''
        response = requests.post(f'{self.api_url}/environment/open', headers={'Authorization': f'ApiKey {self.api_key}'})
        if response.status_code != 200:
            logging.error(f'Could not open new environment {response.status_code}:{response.json()}')
        return response.json()

    def close_env(self):
        '''
        Closes an environment in QServer
        '''
        response = requests.post(f'{self.api_url}/environment/close', headers={'Authorization': f'ApiKey {self.api_key}'})
        if response.status_code != 200:
            logging.error(f'Could not close environment {response.status_code}:{response.json()}')
        return response.json()
    
    def add_item(self, qs_item):
        '''
        Add a new item to the queue
        Args:
            qs_item:    QServer item
        '''
        response = requests.post(f'{self.api_url}/queue/item/add', headers={'Authorization': f'ApiKey {self.api_key}'}, \
                                 json={'item': qs_item})
        if response.status_code != 200:
            logging.error(f'Could not close environment {response.status_code}:{response.json()}')
        return response.json()      


class Scan(BaseModel):
    broker_uid: Optional[str]
    detector: Any
    control: Any
    start: int
    stop: int
    num_steps: int

    def convert_to_qs_item(self):
        '''
        Converts a scan object to a QServer item
        '''
        qs_item = {
            'name': 'scan',
            'args': [self.detector.name, self.control.name, self.start, self.stop, self.num_steps],
            'item_type': 'plan'
        }
        return qs_item
