import logging
import requests
import dash_bootstrap_components as dbc
from dash import html, dcc

from json_editor import JSONParameterEditor


def load_bl_controls(app, controls_url):
    # response = requests.get(controls_url)
    # if response.status_code == 200:
    if False:
        controls = response.json()
        gui_items = JSONParameterEditor(_id={'type': 'parameter_editor'},
                                        json_blob=controls)
        gui_items.init_callbacks(app)
    else:
        # logging.warning(f'Get request from controls api returned: {response.status_code}')
        gui_items = []
    return gui_items


def test_control():
    test_control = [dbc.Container(id='m1-control',
                                 children=[
                                            html.H3('M1 Motor', style={'textAlign': 'center'}),
                                            dbc.Row(children=[
                                                        dbc.Col([dbc.Label('Absolute position', style={'textAlign': 'center'}),
                                                                html.P(id='m1-abs-pos', children=0, style={'textAlign': 'center'})], 
                                                                width=6),
                                                        dbc.Col([dbc.Label('Target position', style={'textAlign': 'center'}),
                                                                html.P(id='m1-target-pos', children=1, style={'textAlign': 'center'})], 
                                                                width=6)],
                                                    justify="center", align="center"),
                                            dbc.Label('Jog', style={'textAlign': 'center'}),
                                            dbc.Row([
                                                dbc.Col(children=dbc.Button(id='m1-left',
                                                                            className="fa fa-chevron-left",
                                                                            style={'width': '100%', 'margin-left': '0rem', 'margin-right': '0rem'}),
                                                        width=2),
                                                dbc.Col([
                                                    dbc.Row([
                                                        dbc.Col(dbc.Input(id="m1-jog", value=0.01,
                                                                  style={'height': '2.5rem', 'width': '100%', 'margin-left': '0rem', 'margin-right': '0rem', 'textAlign': 'center'})),
                                                        dbc.Col(dcc.Dropdown(options=[{'label': 'units', 'value': 'units'}], value='units',
                                                                             style={'height': '2.5rem'}))
                                                        ], no_gutters=True)
                                                    ],
                                                    width=8),
                                                dbc.Col(children=dbc.Button(id='m1-right',
                                                                            className="fa fa-chevron-right",
                                                                            style={'width': '100%', 'margin-left': '0rem', 'margin-right': '0rem'}),
                                                        width=2),
                                            ], 
                                            justify="center", align="center", style={'margin-bottom': '1rem'})
                                        ],
                                 style={'border': 'solid', 'border-color': '#B1B3B3', 'border-width': 1, 'margin-bottom': '2rem'},
                                 fluid=True,
                                ),
                        dbc.Container(id='m1-control2',
                                      children=[
                                        html.H3('M1 Motor', style={'textAlign': 'center'}),
                                        dbc.Row(
                                            [dbc.Col(dbc.Label('Absolute position', style={'textAlign': 'center'})),
                                            dbc.Col(html.P(id='m1-abs-pos2', children=0, style={'textAlign': 'center'}))]
                                        ),
                                        dcc.Slider( min=0,
                                                    max=1,
                                                    step=0.01,
                                                    value=0,
                                                    tooltip={'always_visible': True, 'placement': 'bottom'},
                                                    marks={0: '0units', 0.5: '0.5units', 1:'1units'},
                                                    updatemode='mouseup',
                                                    id='my-slider')],
                                      style={'border': 'solid', 'border-color': '#B1B3B3', 'border-width': 1})
                        ]
    return test_control