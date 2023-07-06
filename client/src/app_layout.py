import os

from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import requests

from src.epics_db.epicsdb_utils import get_ophyd_dash_items
from src.model import BeamlineComponents
from src.helper_utils import comp_list_to_options


class BeamlineComponentsNotFound(Exception):
    pass


#### SETUP DASH APP ####
external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/style.css", 
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "BL 5.3.1"
app._favicon = 'LBL_icon.ico'

# Get beamline PVs from MongoDB as OphydDash object
BL_API_URL = str(os.environ.get('BL_API_URL'))
BL_API_KEY = str(os.environ.get('BL_API_KEY'))
BL_UID = str(os.environ.get('BL_UID'))
response = requests.get(f'{BL_API_URL}/beamline/{BL_UID}/components', headers={"api_key": BL_API_KEY})
if response.status_code != 200:
    raise BeamlineComponentsNotFound(f'Status code: {response.status_code}')
ophyd_items = get_ophyd_dash_items(raw_json=response.json())
COMPONENT_LIST = BeamlineComponents(ophyd_items)
COMPONENT_GUI = COMPONENT_LIST.get_gui()
dropdown_scalers = ['Time'] + COMPONENT_LIST.comp_id_list

### BEGIN DASH CODE ###
# APP HEADER
HEADER = dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col(
                        html.Img(id="app-logo",
                                 src="assets/LBL_logo.png",
                                 height="60px"),
                        md="auto"
                    ),
                    dbc.Col(
                        html.Div(
                            id = 'app-title',
                            children=[html.H3("Advanced Light Source | Beamline 5.3.1")],
                        ),
                        md=True,
                        align="center",
                    )
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.NavbarToggler(id="navbar-toggler"),
                        html.Div(
                            dbc.Nav([
                                dbc.NavItem(
                                    dbc.Button(className="fa fa-github",
                                               style={"font-size": 40, "margin-right": "1rem", "color": "#00313C", "background-color": "white"},
                                               href="https://github.com/als-computing/beamline531")
                                               ),
                                dbc.NavItem(
                                    dbc.Button(className="fa fa-question-circle-o",
                                               style={"font-size": 40, "color": "#00313C", "background-color": "white"},
                                               href="https://github.com/als-computing/beamline531")
                                               )
                            ],
                            navbar=True)
                        )
                    ])
                ])
            ],
            fluid=True),
        dark=True,
        color="#00313C",
        sticky="top"
        )


# BEAMLINE INPUTS (CONTROLS)
BL_INPUT = html.Div(id='bl-controls',
                    children=COMPONENT_GUI)

# STATUS OUTPUT
BL_STATUS = html.Div([
    dcc.Textarea(
        placeholder='Status:',
        id='status_txt',
        value='Status:',
        style={'width': '100%'}
    )
])

# BEAMLINE OUTPUTS (SCANS, CAMERAS, ETC)
BL_OUTPUT = [dbc.Card(
                children=[
                    dbc.CardHeader("Camera"),
                    dbc.CardBody(html.Div([dcc.Graph(id='bl-cam',figure=px.imshow(img=np.zeros((1024,1024))))]))
                    ]
                ),
            dbc.Card(
                children=[
                    dbc.CardHeader("Live scaler"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Axis to plot (x):'),
                                dcc.Dropdown(
                                    id='scaler-x',
                                    options= [{'label': i, 'value':i} for i in dropdown_scalers], 
                                    value = 'Time',
                                    placeholder = 'Select variable for x-axis'
                                    )]
                                ),
                            dbc.Col([
                                dbc.Label('Axis to plot (y):'),
                                dcc.Dropdown(
                                    id='scaler-y',
                                    options=[{'label': i, 'value':i} for i in dropdown_scalers],
                                    placeholder = 'Select variable for y-axis'
                                    )]
                                )], style={'margin-bottom': '1rem'}),
                        dbc.Row([
                            dbc.Col(dcc.Graph(id='scalerPlot',
                                              style={'height':'24rem', "width": "100%", "display": "inline-block" }), width=6),
                        ])
                    ])
                    ]
                ),
             dbc.Card(
                children=[
                    dbc.CardHeader("Scan"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(dcc.Graph(id='scan-img',
                                              style={'height':'24rem', "width": "100%", "display": "inline-block" }), width=6),
                            dbc.Col(dash_table.DataTable(id='scan-output',
                                                         style_cell={'maxWidth': 0,
                                                                     'overflow': 'hidden',
                                                                     'textOverflow': 'ellipsis'}, 
                                                         style_table={'height':'24rem', 'overflowY': 'auto'},
                                                         css=[{"selector": ".show-hide", "rule": "display: none"}],  
                                                         fixed_rows={'headers': False},
                                                         tooltip_duration=None), 
                                    width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Axis to move:'),
                                dcc.Dropdown(
                                    id='control-dropdown',
                                    options=comp_list_to_options(COMPONENT_LIST.find_comp_type('control'))
                                    )]
                                ),
                            dbc.Col([
                                dbc.Label('Axis to scan:'),
                                dcc.Dropdown(
                                    id='detector-dropdown',
                                    options=comp_list_to_options(COMPONENT_LIST.find_comp_type('detector'))
                                    )]
                                ),
                        ], style={'margin-bottom': '1rem'}),
                        dbc.Row(
                            dbc.Col(
                                dash_table.DataTable(id='scan-table',
                                                     columns=[{'name': 'Type', 'id': 'type'},
                                                              {'name': 'Prefix', 'id': 'prefix'}, 
                                                              {'name': 'Name', 'id': 'name'}, 
                                                              {'name': 'ID', 'id': 'id'},
                                                              {'name': 'Start', 'id': 'start'}, 
                                                              {'name': 'Stop', 'id': 'stop'}],
                                                     hidden_columns=['id'],
                                                     row_selectable='single',
                                                     data=[],
                                                     row_deletable=True,
                                                     css=[{"selector": ".show-hide", "rule": "display: none"}],
                                                     style_data_conditional=[
                                                        {'if': {'column_id': 'type', 'filter_query': '{type} = control'},
                                                        'backgroundColor': 'green',
                                                        'color': 'white'},
                                                        {'if': {'column_id': 'type', 'filter_query': '{type} = detector'},
                                                        'backgroundColor': 'blue',
                                                        'color': 'white'}
                                                        ]
                                                    )
                            ), style={'margin-bottom':'1rem', 'margin-top':'1rem'},
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Start:'),
                                    dbc.Input(id='scan-start',
                                              type='number')
                                ], className="mb-3")
                            ]),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Stop:'),
                                    dbc.Input(id='scan-stop',
                                              type='number')
                                ], className="mb-3")
                            ]),
                            dbc.Col(
                                dbc.Button('Modify Selected Row',
                                           id='scan-modify-row',
                                           style={'width': '100%'})
                            )
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Number of points:'),
                                    dbc.Input(id='scan-number',
                                              type='number')
                                ], className="mb-3")
                            ]),
                            dbc.Col(
                                dbc.Button('ABORT',
                                            id='scan-abort',
                                            color="danger",
                                            style={'width': '100%'}),
                            ),
                            dbc.Col(
                                dbc.Button('GO',
                                            id='scan-go',
                                            color="success",
                                            style={'width': '100%'}),
                            ),
                        ]),
                        dbc.Row([BL_STATUS])

                    ]),
                ]
             )
            ]



##### DEFINE LAYOUT #####
app.layout = html.Div(
    [
        HEADER,
        dbc.Container([
                dbc.Row([
                    dbc.Col(BL_INPUT, width=4),
                    dbc.Col(BL_OUTPUT, width=8),
                ]),
                dcc.Interval(id='refresh-interval'),    # time interval to refresh the app, default 1000 milliseconds
                dcc.Store(id='scan-cache', data = None),
                dcc.Store(id='livescaler-cache', data = None),
                # dcc.Store(id='init-live-cache', data = False)
                # dcc.Store(id='bl-cam-data', data=m),
                ],   
                fluid=True
                ),
    ]
)
