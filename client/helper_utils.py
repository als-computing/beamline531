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

###################################################### CLASSES ######################################################

class ComponentType(str, Enum):
    control = "control"
    detector = "detector"


class BasicComponent(BaseModel):
    schema_version: int = 1                         # data schema version
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

    def create_header(self):
        '''
        Creates the header for the GUI component of the component according to it's connection status
        '''
        header = dbc.Row(
                    [dbc.Col(self.name),
                     dbc.Col(daq.PowerButton(id={'base': self.id, 'type': 'on-off'},
                                             on=(self.status=='Online'),
                                             label={'label': self.status, 
                                                    'style': {'margin-left': '1rem', 'margin-top': '0rem',
                                                              'font-size': '15px'}},
                                             size=30,
                                             labelPosition='right',
                                             style={'display': 'inline-block', 'margin-top': '0rem', 
                                                    'margin-bottom': '0rem'}),
                             style={'textAlign': 'right'})
                    ],  
                    justify='center', align='center'
                 )
        return header
    
    def create_sensor_gui(self, current_reading):
        '''
        Creates the GUI components for the sensor
        '''
        status_value = self.status == 'Online'
        header = self.create_header()
        self.gui_comp = [dbc.Card(id={'base': self.id, 'type': 'control'},
                                 children=[
                                    dbc.CardHeader(header),
                                    dbc.CardBody([
                                        # Current position display
                                        dbc.Row(
                                            [dbc.Col(dbc.Label('Current Reading:', style={'textAlign': 'right'})),
                                             dbc.Col(html.P(id={'base': self.id, 'type': 'current-pos'}, 
                                                            children=f'{current_reading}{self.units}', 
                                                            style={'textAlign': 'left'}))],
                                        )
                                    ])
                                ])
                        ]
    
    def create_control_gui(self, current_position):
        '''
        Creates the GUI components for control
        '''
        status_value = self.status == 'Online'
        header = self.create_header()
        self.gui_comp = [dbc.Card(id={'base': self.id, 'type': 'control'},
                                 children=[
                                    dbc.CardHeader(header),
                                    dbc.CardBody([
                                        # Current position display
                                        dbc.Row(
                                            [dbc.Col(dbc.Label('Current Position:', style={'textAlign': 'right'})),
                                             dbc.Col(html.P(id={'base': self.id, 'type': 'current-pos'}, 
                                                            children=f'{current_position}{self.units}', 
                                                            style={'textAlign': 'left'}))],
                                        ),
                                        dbc.Row([
                                            # Absolute move controls
                                            dbc.Col([
                                                dbc.Label(f'Absolute Move ({self.units})', style={'textAlign': 'center'}),
                                                dbc.Row(
                                                    [dbc.Col(
                                                        dcc.Input(id={'base': self.id, 'type': 'target-absolute'}, 
                                                                  min=self.min,
                                                                  max=self.max,
                                                                  step=1,
                                                                  value=current_position, 
                                                                  type='number',
                                                                  disabled=not(status_value),
                                                                  style={'textAlign': 'right', 'width': '90%'})),
                                                    dbc.Col(
                                                        dbc.Button('GO', 
                                                                   id={'base': self.id, 'type': 'target-go'}, 
                                                                   disabled=not(status_value),
                                                                   style={'width': '90%', 'fontSize': '11px'}))],
                                                ), 
                                            ]),
                                            # Relative move controls
                                            dbc.Col([
                                                dbc.Label(f'Relative Move ({self.units})', style={'textAlign': 'center'}),
                                                dbc.Row([
                                                    dbc.Col(
                                                        dbc.Button(id={'base': self.id, 'type': 'target-left'}, 
                                                                   className="fa fa-chevron-left", 
                                                                   style={'width': '90%'}, 
                                                                   disabled=not(status_value)),),
                                                    dbc.Col(
                                                        dcc.Input(id={'base': self.id, 'type': 'target-step'}, 
                                                                  min=self.min,
                                                                  max=self.max,
                                                                  step=0.01,
                                                                  value=1, 
                                                                  type='number',
                                                                  disabled=not(status_value),
                                                                  style={'textAlign': 'right', 'width': '90%'})),
                                                    dbc.Col(
                                                        dbc.Button(id={'base': self.id, 'type': 'target-right'}, 
                                                                   className="fa fa-chevron-right", 
                                                                   style={'width': '90%', 'margin-left': '0rem'}, 
                                                                   disabled=not(status_value))
                                                    )]
                                                ),
                                                # Cache variable to keep track of the target value when a new
                                                # movement is requested before the previous one has completed
                                                dcc.Store(id={'base': self.id, 'type': 'target-value'},
                                                          data=current_position)
                                            ])
                                        ])
                                    ])
                                ])
                        ]

    def connect(self):
        '''
        Defines the GUI representation of the component and initializes it's connection
        '''
        try:
            # Connecting to the component
            if self.type == 'control':
                if self.settle_time:
                    self.comp = EpicsMotor(self.prefix, name=self.name, settle_time=self.settle_time)
                else:
                    self.comp = EpicsMotor(self.prefix, name=self.name)
            else:
                self.comp = EpicsSignal(self.prefix, name=self.name)
            self.comp.wait_for_connection(timeout=self.timeout)
            self.status = 'Online'
            current_reading = self.read()      # update current position
        except Exception as e:
            # the connection was not succesful
            self.status = 'Offline'
            current_reading = 0                # current position goes to 0
            logging.error(f'Component {self.prefix} not found due to: {e}')
        if self.type == 'control':
            self.create_control_gui(current_reading)
        else:
            self.create_sensor_gui(current_reading)
    
    def read(self):
        '''
        Reads the component
        '''
        try:
            reading = self.comp.read()
            return reading[self.name]['value']
        except Exception as e:
            logging.error(f'Could not read component {self.prefix} due to: {e}')
    
    def move(self, target_position):
        '''
        Moves the control to the target position.
        '''
        try:
            self.comp.move(target_position, wait=False)
        except Exception as e:
            logging.error(f'Control {self.prefix} could not move due to: {e}')


class BeamlineComponents():
    def __init__(self, components:'list'):
        self.comp_list = components
        self.comp_id_list = [c.id for c in components]

    def get_gui(self):
        '''
        Retrieves the GUI components
        '''
        # gui_comp_list = [c.gui_comp for c in self.comp_list]
        # Connect to all the components in the beamline
        gui_comp_list = []
        for component in self.comp_list:
            if component.gui_comp is not None:
                # gui_comp_list.append(component.gui_comp)
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

