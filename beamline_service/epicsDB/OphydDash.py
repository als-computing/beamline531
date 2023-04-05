
from happi.client import from_container
import logging, time
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
# %%
class OphydDash():
    _highLimit = 1
    _lowLimit = -1

    def __init__(self, ophydItem):
        # self.name = ophydItem.name
        self.name = ophydItem.extraneous['functional_group']
        self.type = ophydItem.device_class
        self.prefix = ophydItem.prefix
        self.id = ophydItem.extraneous['functional_group']
        self.ophydItem = ophydItem
        self.status = 'Offline'

        self.ophydObj = None
        self.gui_comp = None

        self.connect()
        self.update_status()
        self.set_settle_time()
        self.assignGUI()

    def connect(self):
        try:
            self.ophydObj = from_container(self.ophydItem, attach_md=True)
            time.sleep(0.2)
            self.update_status
        except Exception as e:
            logging.error(f'Could not connect component {self.name} due to: {e}')

    def set_settle_time(self, settleTime = 0.05):
        """
        Set motor settling time 

        Parameters
        ----------
        settleTime : float, optional
            Settling time of motor, default value is 0.05 second
        """
        if self.ophydObj is not None:
            if self.ophydObj.connected:
                self.ophydObj.settle_time = settleTime
            else:
                print(f'{self.name} is not connected')

    def update_status(self):
        """
        Update motor status

        """
        self.status = 'Online' if self.ophydObj.connected else 'Offline'
        self.units = self.ophydObj.egu if self.ophydObj.connected else 'None'
        self.min = self.ophydObj.get_lim(self._lowLimit) if self.ophydObj.connected else 0
        self.max = self.ophydObj.get_lim(self._highLimit) if self.ophydObj.connected else 0
        self.position = self.ophydObj.position if self.ophydObj.connected else np.nan

    def assignGUI(self):
        if self.type == 'ophyd.EpicsMotor':
            create_control_gui(self)
        else:
            create_sensor_gui(self)
            
    def read(self):
        """
        Getting current position 
        """
        if self.ophydObj.connected:
            try:
                return self.ophydObj.position
            except Exception as e:
                logging.error(f'Could not read component {self.name} due to: {e}')
        else:
            logging.error(f'Could not read component {self.name} because it is not connected')        

    def move(self, target_position):
        """
        Move motor to a desire position

        Parameters
        ----------
        target_position : float, required
            Target motor position
        """
        if all([self.ophydObj.connected,
                target_position > self.min,
                target_position < self.max]):
            try:
                self.ophydObj.move(target_position)
            except Exception as e:
                logging.error(f'Could not move component {self.name} due to: {e}')
        else:
            logging.error(f'Could not move component {self.name}. Check if component is connected or the requested position is within range')
            

    
def create_header(obj:'OphydDash'):
    '''
    Creates the header for the GUI component of the component according to it's connection status
    '''
    obj.update_status()
    header = dbc.Row(
                [dbc.Col(obj.name),
                    dbc.Col(daq.PowerButton(id={'base': obj.id, 'type': 'on-off'},
                                            on=(obj.status=='Online'),
                                            label={'label': obj.status, 
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

def create_sensor_gui(obj:'OphydDash', current_reading:'float'=0):
    '''
    Creates the GUI components for the sensor
    '''
    status_value = obj.status == 'Online'
    header = obj.create_header()
    obj.gui_comp = [dbc.Card(id={'base': obj.id, 'type': 'control'},
                                children=[
                                dbc.CardHeader(header),
                                dbc.CardBody([
                                    # Current position display
                                    dbc.Row(
                                        [dbc.Col(dbc.Label('Current Reading:', style={'textAlign': 'right'})),
                                            dbc.Col(html.P(id={'base': obj.id, 'type': 'current-pos'}, 
                                                        children=f'{current_reading}{obj.units}', 
                                                        style={'textAlign': 'left'}))],
                                    )
                                ])
                            ])
                    ]


def create_control_gui(obj:'OphydDash'):
    '''
    Creates the GUI components for control
    '''
    # status_value = self.status == 'Online'
    obj.update_status()
    header = create_header(obj)
    current_position = obj.position
    obj.gui_comp = [dbc.Card(id={'base': obj.id, 'type': 'control'},
                                children=[
                                dbc.CardHeader(header),
                                dbc.CardBody([
                                    # Current position display
                                    dbc.Row(
                                        [dbc.Col(dbc.Label('Current Position:', style={'textAlign': 'right'})),
                                            dbc.Col(html.P(id={'base': obj.id, 'type': 'current-pos'}, 
                                                        children=f'{obj.position if np.isnan(obj.position) else obj.ophydObj.position} {obj.units}', 
                                                        style={'textAlign': 'left'}))],
                                    ),
                                    dbc.Row([
                                        # Absolute move controls
                                        dbc.Col([
                                            dbc.Label(f'Absolute Move ({obj.units})', style={'textAlign': 'center'}),
                                            dbc.Row(
                                                [dbc.Col(
                                                    dcc.Input(id={'base': obj.id, 'type': 'target-absolute'}, 
                                                                min=obj.min,
                                                                max=obj.max,
                                                                step=1,
                                                                value=current_position, 
                                                                type='number',
                                                                disabled=not(obj.status),
                                                                style={'textAlign': 'right', 'width': '90%'})),
                                                dbc.Col(
                                                    dbc.Button('GO', 
                                                                id={'base': obj.id, 'type': 'target-go'}, 
                                                                disabled=not(obj.status),
                                                                style={'width': '90%', 'fontSize': '11px'}))],
                                            ), 
                                        ]),
                                        # Relative move controls
                                        dbc.Col([
                                            dbc.Label(f'Relative Move ({obj.units})', style={'textAlign': 'center'}),
                                            dbc.Row([
                                                dbc.Col(
                                                    dbc.Button(id={'base': obj.id, 'type': 'target-left'}, 
                                                                className="fa fa-chevron-left", 
                                                                style={'width': '90%'}, 
                                                                disabled=not(obj.status)),),
                                                dbc.Col(
                                                    dcc.Input(id={'base': obj.id, 'type': 'target-step'}, 
                                                                min=obj.min,
                                                                max=obj.max,
                                                                step=0.01,
                                                                value=1, 
                                                                type='number',
                                                                disabled=not(obj.status),
                                                                style={'textAlign': 'right', 'width': '90%'})),
                                                dbc.Col(
                                                    dbc.Button(id={'base': obj.id, 'type': 'target-right'}, 
                                                                className="fa fa-chevron-right", 
                                                                style={'width': '90%', 'margin-left': '0rem'}, 
                                                                disabled=not(obj.status))
                                                )]
                                            ),
                                            # Cache variable to keep track of the target value when a new
                                            # movement is requested before the previous one has completed
                                            dcc.Store(id={'base': obj.id, 'type': 'target-value'},
                                                        data=obj.position if np.isnan(obj.position) else obj.ophydObj.position)
                                        ])
                                    ])
                                ])
                            ])
                    ]

