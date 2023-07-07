from dash import html, dcc
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc


def get_cam_layout():
    cam_trigger_mode = ["Continous", "Internal", "External"]
    cam_layout = [
        dbc.CardHeader("Camera"),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("Camera PV:"),
                                            dbc.Input(
                                                id="cam-pv",
                                                type="text",
                                                placeholder="13PIL1",
                                            ),
                                        ],
                                        className="mb-3",
                                    )
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText(
                                                        "Exposure Time (s):"
                                                    ),
                                                    dbc.Input(
                                                        id="cam-exp",
                                                        type="number",
                                                        placeholder="1",
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText("Trigger mode:"),
                                                    dcc.Dropdown(
                                                        id="cam-trig",
                                                        options=[
                                                            {"label": i, "value": i}
                                                            for i in cam_trigger_mode
                                                        ],
                                                        # value=cam_trigger_mode[0],
                                                        placeholder="Select camera trigger mode",
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText(
                                                        "X-pixel (start):"
                                                    ),
                                                    dbc.Input(
                                                        id="xpix-st",
                                                        type="number",
                                                        placeholder="0",
                                                        # style={
                                                        #     "textAlign": "left",
                                                        #     "width": "10%",
                                                        # },
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText(
                                                        "X-pixel (end):"
                                                    ),
                                                    dbc.Input(
                                                        id="xpix-ed",
                                                        type="number",
                                                        placeholder=1024,
                                                        value=1024,
                                                        # style={
                                                        #     "textAlign": "left",
                                                        #     "width": "10%",
                                                        # },
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText(
                                                        "Y-pixel (start):"
                                                    ),
                                                    dbc.Input(
                                                        id="ypix-st",
                                                        type="number",
                                                        placeholder="0",
                                                        # style={
                                                        #     "textAlign": "left",
                                                        #     "width": "10%",
                                                        # },
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText(
                                                        "Y-pixel (end):"
                                                    ),
                                                    dbc.Input(
                                                        id="ypix-ed",
                                                        type="number",
                                                        placeholder=1024,
                                                        value=1024,
                                                        # style={
                                                        #     "textAlign": "left",
                                                        #     "width": "10%",
                                                        # },
                                                    ),
                                                ],
                                                className="mb-3",
                                            )
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("Streaming URL:"),
                                            dbc.Input(
                                                id="stream-url",
                                                type="text",
                                                disabled=True,
                                                placeholder="ws://127.0.0.1:8000/ws/13PIL1",
                                            ),
                                        ],
                                        className="mb-3",
                                    )
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Connect",
                                                id="cam-link",
                                                color="light",
                                                style={"width": "100%"},
                                            ),
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Disconnect",
                                                id="cam-unlink",
                                                color="dark",
                                                style={"width": "100%"},
                                            ),
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("Streaming status:"),
                                            dbc.Textarea(
                                                id="stream-status",
                                                placeholder="Update streaming status",
                                                disabled=True,
                                                style={
                                                    "textAlign": "left",
                                                    "height": 200,
                                                },
                                            ),
                                        ],
                                        className="mb-3",
                                    )
                                ),
                            ],
                            style={
                                "textAlign": "left",
                                "width": "100%",
                            },
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="bl-cam",
                                        figure=px.imshow(img=np.zeros((1024, 1024))),
                                    )
                                ]
                            ),
                        ),
                    ],
                    style={"margin-bottom": "1rem"},
                )
            ]
        ),
    ]
    return cam_layout
