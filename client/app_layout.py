from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from helper_utils import MonoControl


#### SETUP DASH APP ####
external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/style.css", 
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "BL 5.3.1"
app._favicon = 'LBL_icon.ico'

beamline = 'als_5_3_1'
version = '0'
controls_url = f'http://beamline_control:8080/api/v0/beamline/{beamline}/{version}'
MONO_CONTROL = MonoControl(prefix="IOC:m1", name="Mono theta [deg]")
MONO_CONTROL.connect()


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


BL_INPUT = html.Div(id='bl-controls',
                    children=MONO_CONTROL.gui_comp)


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
                    dbc.Col(BL_OUTPUT, width=8),
                ]),
                dcc.Interval(id='refresh-interval')], 
                fluid=True
                ),
    ]
)
