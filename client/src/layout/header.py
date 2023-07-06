from dash import html
import dash_bootstrap_components as dbc
import dash_daq as daq


def component_header(obj: "OphydDash"):
    """
    Creates the header for the GUI component of the component according to it's connection status
    """
    obj.update_status()
    header = dbc.Row(
        [
            dbc.Col(obj.name),
            dbc.Col(
                daq.PowerButton(
                    id={"base": obj.id, "type": "on-off"},
                    on=(obj.status == "Online"),
                    label={
                        "label": obj.status,
                        "style": {
                            "margin-left": "1rem",
                            "margin-top": "0rem",
                            "font-size": "15px",
                        },
                    },
                    size=30,
                    labelPosition="right",
                    style={
                        "display": "inline-block",
                        "margin-top": "0rem",
                        "margin-bottom": "0rem",
                    },
                ),
                style={"textAlign": "right"},
            ),
        ],
        justify="center",
        align="center",
    )
    return header


def app_header(src_app_logo, logo_height, app_title):
    header = dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                id="app-logo", src=src_app_logo, height=logo_height
                            ),
                            md="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                id="app-title",
                                children=[html.H3(app_title)],
                            ),
                            md=True,
                            align="center",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.NavbarToggler(id="navbar-toggler"),
                                html.Div(
                                    dbc.Nav(
                                        [
                                            dbc.NavItem(
                                                dbc.Button(
                                                    className="fa fa-github",
                                                    style={
                                                        "font-size": 40,
                                                        "margin-right": "1rem",
                                                        "color": "#00313C",
                                                        "background-color": "white",
                                                    },
                                                    href="https://github.com/als-computing/beamline531",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.Button(
                                                    className="fa fa-question-circle-o",
                                                    style={
                                                        "font-size": 40,
                                                        "color": "#00313C",
                                                        "background-color": "white",
                                                    },
                                                    href="https://github.com/als-computing/beamline531",
                                                )
                                            ),
                                        ],
                                        navbar=True,
                                    )
                                ),
                            ]
                        )
                    ]
                ),
            ],
            fluid=True,
        ),
        dark=True,
        color="#00313C",
        sticky="top",
    )
    return header
