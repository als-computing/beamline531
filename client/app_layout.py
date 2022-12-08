from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc

from helper_utils import BasicComponent, ComponentType, BeamlineComponents
from helper_utils import comp_list_to_options


#### SETUP DASH APP ####
external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/style.css", 
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "BL 5.3.1"
app._favicon = 'LBL_icon.ico'

# Placeholder for control API
beamline = 'als_5_3_1'
version = '0'
controls_url = f'http://beamline_control:8080/api/v0/beamline/{beamline}/{version}'

# Manually defining the controls for now
mono = BasicComponent(prefix="IOC:m1", name="Mono theta", type=ComponentType('motor'), id="mono", min=0, max=100, units='°')
longitudinal = BasicComponent(prefix="IOC:m3", name="Longitudinal stage", type=ComponentType('motor'), id="long", min=-100, max=100, units='mm')
current = BasicComponent(prefix="bl201-beamstop:current", name="Current", type=ComponentType('signal'), id="current", units="\u03BCA")

COMPONENT_LIST = BeamlineComponents(comp_list=[mono, longitudinal, current])
COMPONENT_GUI = COMPONENT_LIST.get_gui()


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


# BEAMLINE OUTPUTS (SCANS, CAMERAS, ETC)
BL_OUTPUT = [dbc.Card(
                children=[
                    dbc.CardHeader("Camera"),
                    dbc.CardBody(html.Div(id='bl-camera'))
                    ]
                ),
             dbc.Card(
                children=[
                    dbc.CardHeader("Scan"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(dcc.Dropdown(
                                        id='motor-dropdown',
                                        options=comp_list_to_options(COMPONENT_LIST.find_comp_type('motor'))
                                        )
                                    ),
                            dbc.Col(dbc.Button('Add Motor',
                                               id='add-motor',
                                               style={'width': '100%'}),
                                    width=3),
                        ]),
                        dbc.Row(
                            dbc.Col(
                                dash_table.DataTable(id='scan-table',
                                                     columns=[{'name': 'Prefix', 'id': 'prefix'}, 
                                                              {'name': 'Name', 'id': 'name'}, 
                                                              {'name': 'ID', 'id': 'id'},
                                                              {'name': 'Minimum', 'id': 'minimum', 'editable': True}, 
                                                              {'name': 'Step', 'id': 'step', 'editable': True},
                                                              {'name': 'Maximum', 'id': 'maximum', 'editable': True}],
                                                     hidden_columns=['id'],
                                                     row_selectable='single',
                                                     data=[],
                                                     row_deletable=True,
                                                     css=[{"selector": ".show-hide", "rule": "display: none"}]
                                                    )
                            ), style={'margin-bottom':'1rem', 'margin-top':'1rem'},
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Minimum:'),
                                    dbc.Input(id='scan-min',
                                              type='number')
                                ], className="mb-3")
                            ]),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Step:'),
                                    dbc.Input(id='scan-step',
                                              type='number')
                                ], className="mb-3")
                            ]),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Maximum:'),
                                    dbc.Input(id='scan-max',
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
                        ])

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
                dcc.Interval(id='refresh-interval')],   # time interval to refresh the app, default 1000 milliseconds
                fluid=True
                ),
    ]
)
