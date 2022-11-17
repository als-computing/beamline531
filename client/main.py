import json
import requests

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from app_layout import app, MONO_CONTROL


@app.callback(
    Output('m1-abs-pos', 'children'),
    Output('m1-abs-pos2', 'children'),
    Output('m1-target-pos', 'children'),

    Input('m1-left', 'n_clicks'),
    Input('m1-right', 'n_clicks'),
    Input('target-pos', 'value'),
    Input('refresh-interval', 'n_intervals'),

    State('m1-jog', 'value'),
    State('m1-abs-pos', 'children'),

    prevent_initial_call=True
)
def control(m1_left, m1_right, target_position, refresh_int, m1_jog_value, current_pos):
    '''
    This callback reads and moves the mono motor
    Args:
        m1_left:            left-jog button in option 1
        m1_right:           right-job button in option 2
        target_position:    target position slider value in option 2
        refresh_int:        refresh interval
        m1_jog_value:       step value in option 1
        current_pos:        current position in option 1
    Output:
        current position display in option 1
        current position display in option 2
        target position display in option 1
    '''
    changed_id = dash.callback_context.triggered[0]['prop_id']
    # Checks that the motor is connected
    if MONO_CONTROL.status == 'CONNECTED':
        # Left move in option 1
        if changed_id == 'm1-left.n_clicks':
            MONO_CONTROL.move(float(current_pos)-m1_jog_value)
            return dash.no_update, dash.no_update, float(current_pos)-m1_jog_value
        # Right move in option 1
        elif changed_id == 'm1-right.n_clicks': 
            MONO_CONTROL.move(float(current_pos)+m1_jog_value)
            return dash.no_update, dash.no_update, float(current_pos)+m1_jog_value
        # Absolute move in option 2
        elif changed_id == 'target-pos.value': 
            MONO_CONTROL.move(target_position)
            return dash.no_update, dash.no_update, target_position
        # Given the refresh interval, read current position of motor
        else:
            current_pos = MONO_CONTROL.read()
            if current_pos:
                return current_pos, current_pos, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update
    

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
