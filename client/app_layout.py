from dash import Dash, html
import dash_bootstrap_components as dbc

from helper_utils import load_bl_controls


#### SETUP DASH APP ####
external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/style.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "LBL | Beamline 5.3.1"
app._favicon = 'LBL_logo.ico'

beamline = 'als_5_3_1'
version = '0'
controls_url = f'http://beamline_control:8080/api/v0/beamline/{beamline}/{version}'


### BEGIN DASH CODE ###
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
                        html.H3("LBL | Beamline 5.3.1"),
                        md=True,
                        align="center"
                    )
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav([
                                dbc.NavIten(dbc.Button("fa fa-github",
                                               href="https://github.com/als-computing/beamline531")
                                               ),
                                dbc.NavIten(
                                    dbc.Button("fa fa-question-circle-o",
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
        color="dark",
        sticky="top"
        )


BL_INPUT = [dbc.Card(
                id='bl-input',
                children=[
                    dbc.CardHeader("Controls"),
                    dbc.CardBody(html.Div(id='bl-controls',
                                          children=load_bl_controls(controls_url)))
                    ]
                )
            ]


BL_OUTPUT = [dbc.Card(
                children=[
                    dbc.CardHeader("Camera"),
                    dbc.CardBody(html.Div(id='bl-camera'))
                    ]
                ),
             dbc.Card(
                children=[
                    dbc.CardHeader("Scan"),
                    dbc.CardBody(html.Div(id='bl-scan'))
                    ]
                )
            ]


##### DEFINE LAYOUT ####
app.layout = html.Div(
    [
        HEADER,
        dbc.Container([
                dbc.Row([
                    dbc.Col(BL_INPUT, width=4),
                    dbc.Col(BL_OUTPUT, width=8)
                ])], 
                fluid=True
                ),
    ]
)
