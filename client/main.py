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
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if MONO_CONTROL.status == 'CONNECTED':
        if changed_id == 'm1-left.n_clicks':
            MONO_CONTROL.move(float(current_pos)-m1_jog_value)
            return dash.no_update, dash.no_update, float(current_pos)-m1_jog_value
        elif changed_id == 'm1-right.n_clicks':
            MONO_CONTROL.move(float(current_pos)+m1_jog_value)
            return dash.no_update, dash.no_update, float(current_pos)+m1_jog_value
        elif changed_id == 'target-pos.value':
            MONO_CONTROL.move(target_position)
            return dash.no_update, dash.no_update, target_position
        else:
            current_pos = MONO_CONTROL.read()
            if current_pos:
                return current_pos, current_pos, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update
    

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
