import logging
from enum import Enum

from bluesky import RunEngine
from bluesky.plans import scan
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from databroker import Broker
from ophyd import EpicsMotor, EpicsSignal
import pandas as pd
from pydantic import BaseModel, Field
from typing import Any, List, Optional

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Bluesky and databroker setup
RE = RunEngine(context_managers=[])
DB = Broker.named('temp')
RE.subscribe(DB.insert)             # Insert all metadata/data captured into db


class BeamlineComponents():
    def __init__(self, components:'list'):
        self.comp_list = components
        self.comp_id_list = [c.id for c in components]

    def get_gui(self):
        '''
        Retrieves the GUI components
        '''
        # Connect to all the components in the beamline
        gui_comp_list = []
        for component in self.comp_list:
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


class Scan(BaseModel):
    broker_uid: Optional[str]
    detectors: List
    controls: List
    step: int

    def start(self):
        try:
            RE(scan(self.detectors, *self.controls, num=self.step))
        except Exception as e:
            logging.error(f'Error while processing scan: {e}')
        return 
    
    def read(self):
        try:
            scan_summary = DB[-1].table()
        except Exception as e:
            scan_summary = None
            logging.error(f'Error while processing scan: {e}')
        return scan_summary
    
    def stop(self):
        try:
            RE.abort()
        except Exception as e:
            scan_summary = None
            logging.error(f'Error while processing scan: {e}')
        return scan_summary



def comp_list_to_options(comp_list):
    '''
    Converts a list of bluesky components to dash dropwdon options
    Args:
        comp_list:      List of bluesky components
    Returns:
        options:        Dash dropdown options with name and component id
    '''
    options=[]
    for component in comp_list:
        options.append({'label': component.name, 'value': component.id})
    return options


def add2table_remove_from_dropdown(component_list, dropdown_options, data_table, comp_id):
    '''
    Adds new component to scan table and removes this component from it's corresponding dropdown
    Args:
        component_list:     List of components at beamline
        dropdown_options:   Dropdown options for detectors/controls
        data_table:         Details within scan table
        comp_id:            Component ID to add to scan table
    Returns:
        data_table:         Updated table with the component to add
        dropdown_options:   Updated dropdown where the component added to the table is removed
                            from the dropdown
    '''
    component = component_list.find_component(comp_id)
    if component:
        data_table.append(
            {
                'prefix': component.prefix,
                'name': component.name,
                'type': component.type,
                'id': component.id,
                'start': component.min,
                'step': component.step,
                'stop': component.max
            }
        )
    dropdown_options.remove({'label': component.name, 'value': component.id})
    
    return data_table, dropdown_options



def add2dropdown(component_list, control_options, detector_options, data_table, data_table_prev):
    '''
    
    '''
    if len(data_table)==0:
        component = component_list.find_component(data_table_prev[0]['id'])
    else:
        pd_table = pd.DataFrame.from_records(data_table)
        for component in data_table_prev:
            if component['id'] not in list(pd_table['id']):
                component = component_list.find_component(component['id'])
                break
    if component.type == ComponentType('control'):
        control_options = control_options + comp_list_to_options([component])
    else:
        detector_options = detector_options + comp_list_to_options([component])
    return control_options, detector_options

