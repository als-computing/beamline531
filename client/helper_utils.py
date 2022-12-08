import logging
from enum import Enum

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from epics import caget, caput, cainfo
from ophyd import EpicsMotor, EpicsSignal
from pydantic import BaseModel, Field
import requests
from typing import Any, List, Optional, Union


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


###################################################### CLASSES ######################################################

class ComponentType(str, Enum):
    motor = "motor"
    signal = "signal"


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
                    no_gutters=True, justify='center', align='center'
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
    
    def create_motor_gui(self, current_position):
        '''
        Creates the GUI components for motor
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
                                                    no_gutters=True
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
                                                    )], 
                                                    no_gutters=True
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
            if self.type == 'motor':
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
        if self.type == 'motor':
            self.create_motor_gui(current_reading)
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
        Moves the motor to the target position.
        '''
        try:
            self.comp.move(target_position, wait=False)
        except Exception as e:
            logging.error(f'Motor {self.prefix} could not move due to: {e}')


class BeamlineComponents(BaseModel):
    comp_list: List[BasicComponent]

    def get_gui(self):
        '''
        Retrieves the GUI components
        '''
        gui_comp_list = []
        # Connect to all the components in the beamline
        for component in self.comp_list:
            component.connect()
            # Retrieve GUI
            gui_comp_list = gui_comp_list + component.gui_comp
        return gui_comp_list
    
    def find_component(self, base_id):
        '''
        Searches for the corresponding component within the component list based on the 
        value of base_id. If no component is found, returns None
        '''
        for component in self.comp_list:
            if component.id == base_id:
                return component
        logging.error(f'Base id {base_id} was not found among the list of components.')
        return None