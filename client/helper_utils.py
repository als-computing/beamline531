import logging

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from epics import caget, caput, cainfo
from ophyd import EpicsMotor
from pydantic import BaseModel, Field
import requests
from typing import Any, List, Optional


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class BasicSensor(BaseModel):
    schema_version: int = 0         # data schema version
    id: str = Field(description="base id for dash GUI components")
    name: str = Field(description="epics name")
    prefix: str = Field(description="epics prefix")
    units: str = Field(description="units")
    gui_comp: Optional[List] = []   # GUI component
    sensor: Optional[Any] = None    # epics object
    status: str = 'Offline'

    def create_header(self, status_value):
        '''
        Creates the header for the GUI component of the control according to it's connection status
        '''
        header = dbc.Row(
                    [dbc.Col(self.name),
                     dbc.Col([daq.Indicator(labelPosition='right', 
                                            value=status_value, 
                                            label={'label': self.status, 
                                                   'style': {'margin-left': '1rem', 'margin-top': '0rem'}},
                                            style={'display': 'inline-block'}
                              )], 
                             style={'textAlign': 'right'})
                    ], 
                    no_gutters=True, justify='center', align='center'
                 )
        return header
    
    def create_gui(self):
        '''
        Creates the GUI components for the control
        '''
        status_value = self.status == 'Online'
        current_reading = 0
        header = self.create_header(status_value)
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
                                        ),
                                        # ON/OFF Switch
                                        daq.BooleanSwitch(id={'base': self.id, 'type': 'on-off-switch'}, 
                                                          label='ON/OFF',
                                                          on=status_value)
                                    ])
                                ])
                        ]
    
    def read(self):
        '''
        Reads the current position of the sensor
        '''
        try:
            reading = caget(self.prefix)
            return reading
        except Exception as e:
            logging.error(f'Could not read sensor due to: {e}')
    

class BasicControl(BaseModel):
    schema_version: int = 0         # data schema version
    id: str = Field(description="base id for dash GUI components")
    prefix: str = Field(description="epics prefix")
    name: str = Field(description="epics name")
    min: float = Field(description="minimum position")
    max: float = Field(description="maximum position")
    units: str = Field(description="units")
    timeout: Optional[float] = 2.0  # connection timeout
    gui_comp: Optional[List] = []   # GUI component
    control: Optional[Any] = None   # ophyd object
    status: str = 'Offline'         # connection status

    def create_header(self, status_value):
        '''
        Creates the header for the GUI component of the control according to it's connection status
        '''
        header = dbc.Row(
                    [dbc.Col(self.name),
                     dbc.Col([daq.Indicator(labelPosition='right', 
                                            value=status_value, 
                                            label={'label': self.status, 
                                                   'style': {'margin-left': '1rem', 'margin-top': '0rem'}},
                                            style={'display': 'inline-block'}
                              )], 
                             style={'textAlign': 'right'})
                    ], 
                    no_gutters=True, justify='center', align='center'
                 )
        return header
    
    def create_gui(self, current_position):
        '''
        Creates the GUI components for the control
        '''
        status_value = self.status == 'Online'
        header = self.create_header(status_value)
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
                                                          data=0)
                                            ])
                                        ])
                                    ])
                                ])
                        ]


    def connect(self):
        '''
        Defines the GUI representation of the control and initializes it's connection
        '''
        try:
            # Connecting to the motor
            self.control = EpicsMotor(self.prefix, name=self.name)
            self.control.wait_for_connection(timeout=self.timeout)
            self.status = 'Online'
            current_position = self.read()      # update current position
        except Exception as e:
            # the connection was not succesful
            self.status = 'Offline'
            current_position = 0                # current position goes to 0
            logging.error(f'Motor not found due to: {e}')
        self.create_gui(current_position)
    
    def read(self):
        '''
        Reads the current position of the motor
        '''
        try:
            reading = self.control.read()
            return reading[self.name]['value']
        except Exception as e:
            logging.error(f'Could not read motor position due to: {e}')
    
    def move(self, target_position):
        '''
        Moves the motor to the target position
        '''
        try:
            self.control.move(target_position, wait=False)
        except Exception as e:
            logging.error(f'Motor could not move due to: {e}')


def find_control(control_list, base_id):
    '''
    This function searches for the corresponding control within the control list
    based on the value of base_id. If no control is found, returns None
    '''
    for control in control_list:
        if control.id == base_id:
            return control
    logging.error(f'Base id {base_id} was not found among the list of controls.')
    return None
