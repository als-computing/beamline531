import json
import requests

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from app_layout import app, COMPONENT_LIST


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
    control = COMPONENT_LIST.find_component(id_dict['base'])
    # Checks if the control was found succesfully
    if control:
        # Checks that the motor is connected
        if control.status == 'Online':
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
def read_component(refresh_interval, components_ids):
    '''
    This callback reads and updates the position of all the components
    Args:
        refresh_interval:   Time interval between updates
        components_ids:     List of all the components IDs
    Output:
        current reading of all the components
    '''
    response_list = []
    for component_base_id in components_ids:
        component = COMPONENT_LIST.find_component(component_base_id['base'])
        current_read = '0'
        # Checks if the component was found succesfully
        if component:
            current_read = f'0{component.units}'
            # Checks that the motor is connected
            if component.status == 'Online':
                # Given the refresh interval, read component
                reading = component.read()
                if reading:
                    current_read = f'{reading}{component.units}'
        response_list.append(current_read)
    return response_list


@app.callback(
    Output({'base': MATCH, 'type': 'on-off'}, 'on'),
    Output({'base': MATCH, 'type': 'on-off'}, 'label'),

    Input({'base': MATCH, 'type': 'on-off'}, 'on'),

    State({'base': MATCH, 'type': 'on-off'}, 'label'),

    prevent_initial_call=True
)
def turn_on_off(on_off_clicks, current_label):
    '''
    This callback turns components ON/OFF per user's request
    Args:
        on_off_clicks:  Button ON/OFF has been clicked
        current_label:  Current label in component header
    Returns:
        ON/OFF status
        ON/OFF label
    '''
    changed_id = dash.callback_context.triggered[0]['prop_id']
    id_dict = json.loads(changed_id.split('.')[0])     # Get base id of component
    component = COMPONENT_LIST.find_component(id_dict['base'])
    # Checks if the component was found succesfully
    if component:
        # Checks if the component is not connected
        if component.status == 'Offline':
            # Try to connect
            component.connect()
        else:
            component.status = not(component.status)
        current_label['label'] = component.status
        status = component.status
    else:
        status = 'Offline'
    return status == 'Online', current_label        


# @app.callback(
#     Output('scan-output', 'children'),

#     Input('scan-go', 'n_clicks'),
#     Input('scan-abort', 'n_clicks')
# )
# def start_scan(scan_go, scan_abort):
#     '''
#     This callback starts a scan
#     '''

#     from bluesky.plans import count

#     dets = [bl531_current]   # a list of any number of detectors
#     motors = bl531_mono

#     RE(count(dets))

#     from bluesky.plans import scan
#     RE(scan(dets, motors, 20, 21, 11))


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
