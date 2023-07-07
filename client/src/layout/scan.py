from dash import html, dcc, dash_table
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
from helper_utils import comp_list_to_options


def get_scan_layout(component_list, title="Scan"):
    layout = [
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id="scan-img",
                                style={
                                    "height": "24rem",
                                    "width": "100%",
                                    "display": "inline-block",
                                },
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dash_table.DataTable(
                                id="scan-output",
                                style_cell={
                                    "maxWidth": 0,
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                },
                                style_table={
                                    "height": "24rem",
                                    "overflowY": "auto",
                                },
                                css=[
                                    {
                                        "selector": ".show-hide",
                                        "rule": "display: none",
                                    }
                                ],
                                fixed_rows={"headers": False},
                                tooltip_duration=None,
                            ),
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Axis to move:"),
                                dcc.Dropdown(
                                    id="control-dropdown",
                                    options=comp_list_to_options(
                                        component_list.find_comp_type("control")
                                    ),
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Axis to scan:"),
                                dcc.Dropdown(
                                    id="detector-dropdown",
                                    options=comp_list_to_options(
                                        component_list.find_comp_type("detector")
                                    ),
                                ),
                            ]
                        ),
                    ],
                    style={"margin-bottom": "1rem"},
                ),
                dbc.Row(
                    dbc.Col(
                        dash_table.DataTable(
                            id="scan-table",
                            columns=[
                                {"name": "Type", "id": "type"},
                                {"name": "Prefix", "id": "prefix"},
                                {"name": "Name", "id": "name"},
                                {"name": "ID", "id": "id"},
                                {"name": "Start", "id": "start"},
                                {"name": "Step", "id": "step"},
                                {"name": "Stop", "id": "stop"},
                            ],
                            hidden_columns=["id"],
                            row_selectable="single",
                            data=[],
                            row_deletable=True,
                            css=[
                                {
                                    "selector": ".show-hide",
                                    "rule": "display: none",
                                }
                            ],
                            style_data_conditional=[
                                {
                                    "if": {
                                        "column_id": "type",
                                        "filter_query": "{type} = control",
                                    },
                                    "backgroundColor": "green",
                                    "color": "white",
                                },
                                {
                                    "if": {
                                        "column_id": "type",
                                        "filter_query": "{type} = detector",
                                    },
                                    "backgroundColor": "blue",
                                    "color": "white",
                                },
                            ],
                        )
                    ),
                    style={"margin-bottom": "1rem", "margin-top": "1rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Start:"),
                                        dbc.Input(id="scan-start", type="number"),
                                    ],
                                    className="mb-3",
                                )
                            ]
                        ),
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Step:"),
                                        dbc.Input(id="scan-step", type="number"),
                                    ],
                                    className="mb-3",
                                )
                            ]
                        ),
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Stop:"),
                                        dbc.Input(id="scan-stop", type="number"),
                                    ],
                                    className="mb-3",
                                )
                            ]
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Modify Selected Row",
                                id="scan-modify-row",
                                style={"width": "100%"},
                            )
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                "ABORT",
                                id="scan-abort",
                                color="danger",
                                style={"width": "100%"},
                            ),
                        ),
                        dbc.Col(
                            dbc.Button(
                                "GO",
                                id="scan-go",
                                color="success",
                                style={"width": "100%"},
                            ),
                        ),
                    ]
                ),
            ]
        ),
    ]
    return layout
