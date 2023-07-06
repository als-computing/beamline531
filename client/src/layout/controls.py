from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
from layout.header import component_header


def get_controls_layout(component_gui):
    bl_input = html.Div(id="bl-controls", children=component_gui)
    return bl_input


def create_control_gui(obj: "OphydDash"):
    """
    Creates the GUI components for control
    """
    # status_value = self.status == 'Online'
    obj.update_status()
    header = component_header(obj)
    current_position = np.round(obj.position, obj.precision)
    obj.gui_comp = [
        dbc.Card(
            id={"base": obj.id, "type": "control"},
            children=[
                dbc.CardHeader(header),
                dbc.CardBody(
                    [
                        # Current position display
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label(
                                        "Current Position:",
                                        style={"textAlign": "right"},
                                    )
                                ),
                                dbc.Col(
                                    html.P(
                                        id={"base": obj.id, "type": "current-pos"},
                                        children=f"{obj.position if np.isnan(obj.position) else obj.ophydObj.position} {obj.unit}",
                                        style={"textAlign": "left"},
                                    )
                                ),
                            ],
                        ),
                        dbc.Row(
                            [
                                # Absolute move controls
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            f"Absolute Move ({obj.unit})",
                                            style={"textAlign": "center"},
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dcc.Input(
                                                        id={
                                                            "base": obj.id,
                                                            "type": "target-absolute",
                                                        },
                                                        # min=obj.min,
                                                        # max=obj.max,
                                                        value=current_position,
                                                        type="number",
                                                        disabled=not (obj.status),
                                                        style={
                                                            "textAlign": "right",
                                                            "width": "90%",
                                                        },
                                                    )
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        "GO",
                                                        id={
                                                            "base": obj.id,
                                                            "type": "target-go",
                                                        },
                                                        disabled=not (obj.status),
                                                        style={
                                                            "width": "90%",
                                                            "fontSize": "11px",
                                                        },
                                                    )
                                                ),
                                            ],
                                        ),
                                    ]
                                ),
                                # Relative move controls
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            f"Relative Move ({obj.unit})",
                                            style={"textAlign": "center"},
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        id={
                                                            "base": obj.id,
                                                            "type": "target-left",
                                                        },
                                                        className="fa fa-chevron-left",
                                                        style={"width": "90%"},
                                                        disabled=not (obj.status),
                                                    ),
                                                ),
                                                dbc.Col(
                                                    dcc.Input(
                                                        id={
                                                            "base": obj.id,
                                                            "type": "target-step",
                                                        },
                                                        # min=obj.min,
                                                        # max=obj.max,
                                                        # step=0.01,
                                                        value=1,
                                                        type="number",
                                                        disabled=not (obj.status),
                                                        style={
                                                            "textAlign": "right",
                                                            "width": "90%",
                                                        },
                                                    )
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        id={
                                                            "base": obj.id,
                                                            "type": "target-right",
                                                        },
                                                        className="fa fa-chevron-right",
                                                        style={
                                                            "width": "90%",
                                                            "margin-left": "0rem",
                                                        },
                                                        disabled=not (obj.status),
                                                    )
                                                ),
                                            ]
                                        ),
                                        # Cache variable to keep track of the target value when a new
                                        # movement is requested before the previous one has completed
                                        dcc.Store(
                                            id={"base": obj.id, "type": "target-value"},
                                            data=obj.position
                                            if np.isnan(obj.position)
                                            else obj.ophydObj.position,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        )
    ]
