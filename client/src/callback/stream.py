from dash.dependencies import Input, Output, State
from dash.dependencies import ClientsideFunction
from callback.pva_monitor import pvaMonitor

# from splash_streamer.splash_streamer.data_sources.pva_monitor import pvaMonitor


def camStream(app, cam_pva):
    @app.callback(
        Output("stream-status", "value", allow_duplicate=True),
        Output("ws", "url"),
        Input("cam-stream", "n_clicks"),
        State("stream-url", "value"),
        prevent_initial_call="initial_duplicate",
    )
    def _camStream(cam_stream, stream_url):
        msg = ""

        # Front end
        msg += f"Creating websocket: {stream_url}"

        return "ws://streamer_api:8000/ws/pva", "ws://streamer_api:8000/ws/pva"

    @app.callback(
        Output("stream-status", "value", allow_duplicate=True),
        Input("ws", "url"),
        prevent_initial_call=True,
    )
    def _printws(ws):
        return ws

    @app.callback(
        Output("stream-status", "value", allow_duplicate=True),
        Input("ws", "message"),
        prevent_initial_call="initial_duplicate",
    )
    def _print_ws_msg(msg):
        m = f"Getting ws msg: {msg}"
        return m
