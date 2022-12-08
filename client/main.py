import json
import requests

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from app_layout import app, COMPONENT_LIST
from helper_utils import comp_list_to_options


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
            component.status = 'Offline'
        current_label['label'] = component.status
        status = component.status
    else:
        status = 'Offline'
    return status == 'Online', current_label        


@app.callback(
    Output('scan-table', 'data'),
    Output('motor-dropdown', 'options'),

    Input('add-motor', 'n_clicks'),
    Input('scan-modify-row', 'n_clicks'),
    Input('scan-table', 'data_previous'),
    
    State('motor-dropdown', 'value'),
    State('motor-dropdown', 'options'),
    State('scan-table', 'data'),
    State('scan-table', 'selected_rows'),
    State('scan-min', 'value'),
    State('scan-step', 'value'),
    State('scan-max', 'value'),
    prevent_initial_call=True
)
def manage_scantable(add_motor, modify_row, data_table_prev, motor_id, dropdown_options, 
                     data_table, selected_rows, scan_min, scan_step, scan_max):
    '''
    This callback manages the setup of the scan table
    Args:
        add_motor:              Add motor button has been clicked
        modify_row:             Modify row button has been clicked
        data_table_prev:        Previous data in scan table, which is used to detect the deletion
                                of rows (motors)
        motor_id:               ID of motor selected from the dropdown options
        dropdown_options:       Current dropdown options, these options will update according to
                                the entries in the scan table
        data_table:             Data in scan table
        selected_rows:          Indexes of selected rows
        scan_min:               Minimum value for the selected motor
        scan_step:              Step value for the selected motor
        scan_max:               Maximum value for the selected motor
    Returns:
        data_table:             Updated data in scan table
        dropdown_options:       Updated dropdown options
    '''
    changed_id = dash.callback_context.triggered[0]['prop_id']
    # Adds a motor
    if 'add-motor' in changed_id:
        motor = COMPONENT_LIST.find_component(motor_id)
        if motor:
            data_table.append(
                {
                    'prefix': motor.prefix,
                    'name': motor.name,
                    'id': motor.id,
                    'minimum': motor.min,
                    'step': 1,
                    'maximum': motor.max
                }
            )
        dropdown_options.remove({'label': motor.name, 'value': motor.id})
    # Modifies the selected row
    elif 'scan-modify-row' in changed_id:
        if selected_rows:
            data_table[selected_rows[0]]['minimum'] = scan_min
            data_table[selected_rows[0]]['step'] = scan_step
            data_table[selected_rows[0]]['maximum'] = scan_max
    # Updates dropdown options if a row has been deleted
    elif len(data_table_prev)>len(data_table):
        for motor in data_table_prev:
            if motor['id'] not in data_table:
                motor = COMPONENT_LIST.find_component(motor['id'])
                break
        dropdown_options = dropdown_options + comp_list_to_options([motor])
        data_table = dash.no_update
    return data_table, dropdown_options


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
