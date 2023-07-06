from dash import html, dcc
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc


def get_scaler_layout(dropdown_scalers, title="Live scaler"):
    layout = [
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Axis to plot (x):"),
                                dcc.Dropdown(
                                    id="scaler-x",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in dropdown_scalers
                                    ],
                                    value="Time",
                                    placeholder="Select variable for x-axis",
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Axis to plot (y):"),
                                dcc.Dropdown(
                                    id="scaler-y",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in dropdown_scalers
                                    ],
                                    placeholder="Select variable for y-axis",
                                ),
                            ]
                        ),
                    ],
                    style={"margin-bottom": "1rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id="scalerPlot",
                                style={
                                    "height": "24rem",
                                    "width": "100%",
                                    "display": "inline-block",
                                },
                            ),
                            width=6,
                        ),
                    ]
                ),
            ]
        ),
    ]
    return layout
