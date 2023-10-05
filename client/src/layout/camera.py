from dash import html, dcc
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
from dash_extensions import WebSocket


def get_cam_layout(cam_list):
    cam_name_list = cam_list.comp_id_list
    cam_trigger_mode = ["Single", "Multiple", "Continous"]
    url = 'ws://localhost:8000/ws/pva' #'ws://streamer_api:8000/ws/pva'
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
                                            dcc.Dropdown(
                                                id="cam-pv",
                                                options=[
                                                    {"label": i, "value": i}
                                                    for i in cam_name_list
                                                ],
                                                placeholder="Select camera or detector",
                                                value=cam_name_list[0],
                                                style={"width": "70%"},
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
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
                                                    dbc.InputGroupText("Image mode:"),
                                                    dcc.Dropdown(
                                                        id="img-mode",
                                                        options=[
                                                            {"label": i, "value": i}
                                                            for i in cam_trigger_mode
                                                        ],
                                                        placeholder="Select camera image mode",
                                                        style={"width": "50%"},
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
                                    ]
                                ),
                                dbc.Row(
                                    [
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
                                            html.Div([WebSocket(id="ws", url=url)])
                                        ],
                                        className="mb-3",
                                    )
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Acquire",
                                                id="cam-acquire",
                                                color="light",
                                                style={"width": "100%"},
                                            ),
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Stop",
                                                id="cam-stop",
                                                color="dark",
                                                style={"width": "100%"},
                                            ),
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Streaming",
                                                id="cam-stream",
                                                color="light",
                                                style={"width": "100%"},
                                            ),
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Streaming Reset",
                                                id="stream-reset",
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
                                            dbc.InputGroupText("Camera status:"),
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
                                    ),
                                    html.Div(id="render-time"),
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
