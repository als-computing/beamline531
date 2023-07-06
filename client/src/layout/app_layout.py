from dash import html, dcc
import dash_bootstrap_components as dbc
from layout.header import app_header
from layout.camera import get_cam_layout
from layout.controls import get_controls_layout
from layout.scaler import get_scaler_layout
from layout.scan import get_scan_layout


def get_app_layout(
    component_list,
    component_gui,
    dropdown_scalers,
    src_app_logo="assets/LBL_logo.png",
    logo_height="60px",
    app_title="Advanced Light Source | Beamline 5.3.1",
):
    ##### DEFINE LAYOUT #####
    layout = html.Div(
        [
            app_header(src_app_logo, logo_height, app_title),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(get_controls_layout(component_gui), width=4),
                            dbc.Col(
                                sensing(component_list, dropdown_scalers),
                                width=8,
                            ),
                        ]
                    ),
                    dcc.Interval(id="refresh-interval"),
                    dcc.Store(id="scan-cache", data=None),
                    dcc.Store(id="livescaler-cache", data=None),
                ],
                fluid=True,
            ),
        ]
    )
    return layout


# def header(src_app_logo, logo_height, app_title):
#     header = dbc.Navbar(
#         dbc.Container(
#             [
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             html.Img(
#                                 id="app-logo", src=src_app_logo, height=logo_height
#                             ),
#                             md="auto",
#                         ),
#                         dbc.Col(
#                             html.Div(
#                                 id="app-title",
#                                 children=[html.H3(app_title)],
#                             ),
#                             md=True,
#                             align="center",
#                         ),
#                     ]
#                 ),
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             [
#                                 dbc.NavbarToggler(id="navbar-toggler"),
#                                 html.Div(
#                                     dbc.Nav(
#                                         [
#                                             dbc.NavItem(
#                                                 dbc.Button(
#                                                     className="fa fa-github",
#                                                     style={
#                                                         "font-size": 40,
#                                                         "margin-right": "1rem",
#                                                         "color": "#00313C",
#                                                         "background-color": "white",
#                                                     },
#                                                     href="https://github.com/als-computing/beamline531",
#                                                 )
#                                             ),
#                                             dbc.NavItem(
#                                                 dbc.Button(
#                                                     className="fa fa-question-circle-o",
#                                                     style={
#                                                         "font-size": 40,
#                                                         "color": "#00313C",
#                                                         "background-color": "white",
#                                                     },
#                                                     href="https://github.com/als-computing/beamline531",
#                                                 )
#                                             ),
#                                         ],
#                                         navbar=True,
#                                     )
#                                 ),
#                             ]
#                         )
#                     ]
#                 ),
#             ],
#             fluid=True,
#         ),
#         dark=True,
#         color="#00313C",
#         sticky="top",
#     )
#     return header


# BEAMLINE OUTPUTS (SCANS, CAMERAS, ETC)
def sensing(component_list, dropdown_scalers):
    sensing_layout = [
        dbc.Card(children=get_cam_layout()),
        dbc.Card(children=get_scaler_layout(dropdown_scalers)),
        dbc.Card(children=get_scan_layout(component_list)),
    ]
    return sensing_layout
