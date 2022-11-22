import logging

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from ophyd import EpicsMotor
from pydantic import BaseModel
import requests
from typing import Any, List, Optional


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class MonoControl(BaseModel):
    schema_version: int = 0
    prefix: str
    name: str
    timeout: Optional[float] = 2.0
    gui_comp: Optional[List] = []
    control: Optional[Any] = None
    status: str = 'DISCONNECTED'

    def connect(self):
        '''
        Defines the GUI representation of the control and initializes it's connection
        '''
        try:
            # Connecting to the motor
            self.control = EpicsMotor(self.prefix, name=self.name)
            self.control.wait_for_connection(timeout=self.timeout)
            self.status = 'CONNECTED'
            current_position = self.read()      # update current position
            disable = False                     # the action buttons are not disabled
        except Exception as e:
            # the connection was not succesful
            self.status = 'DISCONNECTED'
            current_position = 0                # current position goes to 0
            disable = True                      # disable action buttons
            logging.error(f'Motor not found due to: {e}')
        # GUI component definition
        status_value = self.status == 'CONNECTED'
        self.gui_comp =[dbc.Card(id='m1-control',       # OPTION 1
                                 children=[
                                        dbc.CardHeader(dbc.Row([
                                                        dbc.Col('MONO THETA OPTION 1'),
                                                        dbc.Col(daq.Indicator(labelPosition="right", value=status_value, style={'display': 'inline-block'}, 
                                                                label={"label": self.status, "style": {"margin-left": "1rem", "margin-top": "0rem"}}),
                                                                width=3)
                                                        ], no_gutters=True, justify="center", align="center")
                                                      ),
                                        dbc.CardBody([
                                            dbc.Row(children=[
                                                        dbc.Col([dbc.Label('CURRENT POSITION', style={'textAlign': 'center'}),
                                                                html.P(id='m1-abs-pos', children=f'{current_position}°', style={'textAlign': 'center'})], 
                                                                width=6),
                                                        dbc.Col([dbc.Label('TARGET POSITION', style={'textAlign': 'center'}),
                                                                html.P(id='m1-target-pos', children=f'{current_position}°', style={'textAlign': 'center'})], 
                                                                width=6)],
                                                    justify="center", align="center"),
                                            dbc.Label('JOG', style={'textAlign': 'center'}),
                                            dbc.Row([
                                                dbc.Col(children=dbc.Button(id='m1-left', className="fa fa-chevron-left", style={'width': '90%'}, disabled=disable), width=2),
                                                dbc.Col([
                                                    dbc.Row([
                                                        dbc.Col(dbc.Input(id="m1-jog", value=1, style={'height': '2.5rem', 'width': '100%', 'textAlign': 'center'})),
                                                        dbc.Col(html.H6('deg [°]', style={'margin-left': '0rem', 'textAlign': 'right'}), width=4)
                                                        ], no_gutters=True, justify="center", align="center")
                                                    ],
                                                    width=4),
                                                dbc.Col(children=dbc.Button(id='m1-right', className="fa fa-chevron-right", style={'width': '90%'}, disabled=disable), width=2),
                                            ], justify="center", align="center", style={'margin-bottom': '1rem'})
                                        ])
                                    ],
                                ),
                         dbc.Card(id='m1-control2',     # OPTION 2
                                  children=[
                                        dbc.CardHeader(dbc.Row([
                                                        dbc.Col('MONO THETA OPTION 2'),
                                                        dbc.Col([daq.Indicator(labelPosition="right", value=status_value, 
                                                                              label={"label": self.status, "style": {"margin-left": "1rem", "margin-top": "0rem"}},
                                                                              style={'display': 'inline-block'}
                                                                            )],
                                                                width=3)
                                                        ], no_gutters=True, justify="center", align="center")
                                                      ),
                                        dbc.CardBody([
                                            dbc.Row(
                                                [dbc.Col(dbc.Label('Current position', style={'textAlign': 'center'})),
                                                 dbc.Col(html.P(id='m1-abs-pos2', children=f'{current_position}°', style={'textAlign': 'center'}))]
                                            ),
                                            dbc.Label('Target Position'),
                                            dcc.Slider(id='target-pos', min=0, max=100, step=1, value=current_position, tooltip={'always_visible': True, 'placement': 'bottom'},
                                                       marks={0: '0°', 25: '25°', 50: '50°', 75: '75°', 100:'100°'}, updatemode='mouseup', disabled=disable)
                                        ])
                                    ],
                                )
                        ]
    
    def move(self, target_position):
        '''
        Move the motor to the target position
        '''
        try:
            self.control.move(target_position, wait=False)
        except Exception as e:
            logging.error(f'Motor could not move due to: {e}')

    def read(self):
        '''
        Read the current position of the motor
        '''
        try:
            reading = self.control.read()
            return reading[self.name]['value']
        except Exception as e:
            logging.error(f'Could not read motor position due to: {e}')
