import json
import requests

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from app_layout import app, CONTROL_LIST
from helper_utils import find_control


@app.callback(
    Output({'base': MATCH, 'type':'target-value'}, 'data'),

    Input({'base': MATCH, 'type':'target-go'}, 'n_clicks'),
    Input({'base': MATCH, 'type':'target-left'}, 'n_clicks'),
    Input({'base': MATCH, 'type':'target-right'}, 'n_clicks'),
    
    State({'base': MATCH, 'type':'target-step'}, 'value'),
    State({'base': MATCH, 'type':'target-absolute'}, 'value'),
    State({'base': MATCH, 'type':'target-value'}, 'data'),

    prevent_initial_call=True
)
def move_control(target_go, target_left, target_right, target_step, target_absolute, current_target):
    '''
    This callback reads and moves the motor
    Args:
        target_go:          GO button has been clicked, move to absolute position
        target_left:        LEFT button has been clicked, move to -1 x step size from current 
                            target position
        target_right:       RIGHT button has been clicked, move to +1 x step size from current 
                            target position
        target_step:        step size value for relative target move
        target_absolute:    absolute target position
        current_target:     current target position, this cache value prevents the app from
                            moving to the wrong position when the user requests a new movement
                            before the previous one has completed
    Output:
        current target position
    '''
    changed_id = dash.callback_context.triggered[0]['prop_id']
    id_dict = json.loads(changed_id.split('.')[0])     # Get base id of control
    control = find_control(CONTROL_LIST, id_dict['base'])
    # Checks if the control was found succesfully
    if control:
        # Checks that the motor is connected
        if control.status == 'CONNECTED':
            # Move to absolute position
            if 'target-go' in changed_id:
                if target_absolute: 
                    current_target = target_absolute
            # Move to relative position
            elif target_step:   # checks that the step size is a valid value (e.g. nonnegative)
                if 'target-left' in changed_id and (current_target - target_step)>=control.min:
                    current_target = current_target - target_step
                elif 'target-right' in changed_id and (current_target + target_step)<=control.max:
                    current_target = current_target + target_step
            control.move(current_target)
    return current_target
    

@app.callback(
    Output({'base': ALL, 'type': 'current-pos'}, 'children'),

    Input('refresh-interval', 'n_intervals'),

    State({'base': ALL, 'type': 'current-pos'}, 'id'),
)
def read_position(refresh_interval, controls_ids):
    '''
    This callback reads and updates the position of all the controls
    Args:
        refresh_interval:   Time interval between updates
        controls_ids:       List of all the controls IDs
    Output:
        current position of all the controls
    '''
    response_list = []
    for control_base_id in controls_ids:
        current_pos = dash.no_update
        control = find_control(CONTROL_LIST, control_base_id['base'])
        # Checks if the control was found succesfully
        if control:
            # Checks that the motor is connected
            if control.status == 'CONNECTED':
                # Given the refresh interval, read current position of motor
                reading = control.read()
                if reading:
                    current_pos = f'{current_pos}{control.units}'
        response_list.append(current_pos)
    return response_list
    

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
