import json
import requests

import bluesky
from bluesky import RunEngine
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
from ophyd import EpicsMotor

from app_layout import app


RE = RunEngine({})


@app.callback(
    Output('m1-abs-pos', 'children'),
    Output('m1-target-pos', 'children'),

    Input('m1-left', 'n_clicks'),
    Input('m1-right', 'n_clicks'),
    Input('refresh-interval', 'n_intervals'),

    State('m1-jog', 'value'),
    State('m1-abs-pos', 'children')
)
def control(m1_left, m1_right, refresh_int, m1_jog_value, current_pos):
    changed_id = dash.callback_context.triggered[0]['prop_id']
    # read motor
    try:
        bl531_mono = EpicsMotor('IOC:m1', name='Mono theta [deg]')  # most likely this will have to be performed once
        bl531_mono.wait_for_connection(timeout=2.0)                 # most likely this will have to be performed once
    except Exception as e:
        # print(f'Motor not found due to: {e}')
        pass
    if changed_id == 'm1-left.n_clicks':
        bl531_mono.move(float(current_pos)-m1_jog_value)
        return dash.no_update, float(current_pos)-m1_jog_value
    elif changed_id == 'm1-right.n_clicks':
        bl531_mono.move(float(current_pos)+m1_jog_value)
        return dash.no_update, float(current_pos)+m1_jog_value
    else:
        return bl531_mono.read(), dash.no_update
    

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
