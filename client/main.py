import json
import requests

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from app_layout import app, COMPONENT_LIST
from helper_utils import Scan, ComponentType, add2table_remove_from_dropdown, add2dropdown, RE, DB
import plotly.express as px
from ophyd.sim import det1, det2, motor
from bluesky.plans import scan
import asyncio


@app.callback(
    Output({'base': MATCH, 'type':'target-value'}, 'data'),
    Output({'base': MATCH, 'type':'target-go'}, 'n_clicks'),
    Output({'base': MATCH, 'type':'target-left'}, 'n_clicks'),
    Output({'base': MATCH, 'type':'target-right'}, 'n_clicks'),

    Input({'base': MATCH, 'type':'target-go'}, 'n_clicks'),
    Input({'base': MATCH, 'type':'target-left'}, 'n_clicks'),
    Input({'base': MATCH, 'type':'target-right'}, 'n_clicks'),
    Input({'base': MATCH, 'type':'target-go'}, 'id'),
    State({'base': MATCH, 'type':'target-step'}, 'value'),
    State({'base': MATCH, 'type':'target-absolute'}, 'value'),

    prevent_initial_call=True
)
def move(target_go=None, target_left=None, target_right=None,
                  target_id=None, target_step=0, target_absolute=0):
    '''
    This callback reads and moves the control
    Args:
        target-go:        GO button has been clicked
        target-left:      LEFT arrow has been clicked
        target-right:     RIGHT arrow has been clicked
        target-go_id:     Motor name associated with the button
        target-step:      Value of interval movement
        target-absolute:  Value of target motor position

    Output:
        current target position
    '''
    component_name = target_id['base']
    component_ophyd = COMPONENT_LIST.find_component(component_name)
    current_pos = component_ophyd.ophydObj.position
    if target_go:
        target_pos = target_absolute
    else:
        target_pos = (current_pos - target_step) if target_left else (current_pos + target_step)
    
    component_ophyd.move(target_pos)
    msg = f'Move {component_name} from {current_pos} to {target_pos}'
    return msg, None, None, None
    

@app.callback(
    Output({'base': ALL, 'type': 'current-pos'}, 'children'),
    Input('refresh-interval', 'n_intervals'),
)
def update(refresh_interval):
    '''
    This callback reads and updates the position of all the components
    Args:
        refresh_interval:   Time interval between updates
        
    Output:
        current reading of all the components
    '''
    comp_list = COMPONENT_LIST.comp_list
    
    # Update component status
    for c in comp_list: c.update_status()

    # Get current position
    response_list = ['%.2f %s'%(c.position,c.units) for c in comp_list]
    
    return response_list


@app.callback(
    Output({'base': MATCH, 'type': 'on-off'}, 'on'),
    Output({'base': MATCH, 'type': 'on-off'}, 'label'),

    Input({'base': MATCH, 'type': 'on-off'}, 'on'),
    Input({'base': MATCH, 'type':'on-off'}, 'id'),
    State({'base': MATCH, 'type': 'on-off'}, 'label'),

    prevent_initial_call=True
)
def turn_on_off(on_off_clicks, click_id, current_label):
    '''
    This callback turns components ON/OFF per user's request
    Args:
        on_off_clicks:  Button ON/OFF has been clicked
        click_id:       ID of the button component
        current_label:  Current label in component header
    Returns:
        ON/OFF status
        ON/OFF label
    '''

    component = COMPONENT_LIST.find_component(click_id['base'])
    # Checks if the component was found succesfully
    if component is not None:
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
    Output('control-dropdown', 'options'),
    Output('detector-dropdown', 'options'),
    Output('control-dropdown', 'value'),
    Output('detector-dropdown', 'value'),
    Output('scan-start', 'disabled'),
    Output('scan-step', 'disabled'),
    Output('scan-stop', 'disabled'),
    Output('scan-modify-row', 'disabled'),

    Input('control-dropdown', 'value'),
    Input('detector-dropdown', 'value'),
    Input('scan-modify-row', 'n_clicks'),
    Input('scan-table', 'data_previous'),
    Input('scan-table', 'selected_rows'),

    State('control-dropdown', 'options'),
    State('detector-dropdown', 'options'),
    State('scan-table', 'data'),
    State('scan-start', 'value'),
    State('scan-step', 'value'),
    State('scan-stop', 'value'),
    prevent_initial_call=True
)
def manage_scan_table(control_id, detector_id, modify_row, data_table_prev, selected_rows, control_options, 
                      detector_options, data_table, scan_start, scan_step, scan_stop):
    '''
    This callback manages the setup of the scan table
    Args:
        add_comp:               Add control button has been clicked
        modify_row:             Modify row button has been clicked
        data_table_prev:        Previous data in scan table, which is used to detect the deletion
                                of rows (controls)
        selected_rows:          Indexes of selected rows
        comp_id:                ID of control selected from the dropdown options
        dropdown_options:       Current dropdown options, these options will update according to
                                the entries in the scan table
        data_table:             Data in scan table
        scan_start:             Start value for the selected control
        scan_step:              Step value for the selected control
        scan_stop:              Stop value for the selected control
    Returns:
        data_table:             Updated data in scan table
        dropdown_options:       Updated dropdown options
    '''
    changed_id = dash.callback_context.triggered[0]['prop_id']
    disable_all = dash.no_update
    # Adds a component to scan setup
    if 'control-dropdown' in changed_id:
        data_table, control_options = add2table_remove_from_dropdown(COMPONENT_LIST, control_options, data_table, control_id)
    elif 'detector-dropdown' in changed_id:
        data_table, detector_options = add2table_remove_from_dropdown(COMPONENT_LIST, detector_options, data_table, detector_id)
    # Checks if the selected row is a detector. If this is the case, min/step/max/modify is disabled
    elif 'data_previous' in changed_id:
        control_options, detector_options = add2dropdown(COMPONENT_LIST, control_options, detector_options, data_table, data_table_prev)
    elif 'selected_rows' in changed_id:
        if len(selected_rows)>0:
            if data_table[selected_rows[0]]['type'] == 'detector':
                disable_all = True
            else:
                disable_all = False
        # Updates dropdown options if a row has been deleted
        if len(data_table) + len(control_options) + len(detector_options) != len(COMPONENT_LIST.comp_list):
            control_options, detector_options = add2dropdown(COMPONENT_LIST, control_options, detector_options, data_table, data_table_prev)
    # Modifies the selected row
    elif 'scan-modify-row' in changed_id:
        if selected_rows:
            data_table[selected_rows[0]]['start'] = scan_start
            data_table[selected_rows[0]]['step'] = scan_step
            data_table[selected_rows[0]]['stop'] = scan_stop
    return [data_table, control_options, detector_options, None, None] + [disable_all]*4


@app.callback(
    Output('scan-cache', 'data'),

    Input('scan-go', 'n_clicks'),

    State('scan-table', 'data'),
    prevent_initial_call=True
)
def start_scan(scan_go, scan_table):
    '''
    This callback starts a scan
    Args:
        scan_go:        Go button to start a scan
        scan_table:     Scan details in table
    Return:
        scan_cache:     Scan cache
    '''
    detectors = []
    controls = []
    for row in scan_table:
        if row['type'] == 'detector':
            detectors.append(COMPONENT_LIST.find_component(row['id']).comp)
        else:
            controls = controls + [COMPONENT_LIST.find_component(row['id']).comp, row['start'], row['stop']]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        scans = Scan(detectors=detectors, controls=controls, step=row['step'])
        scans.start()
    except Exception as e:
        print(f'Scan failed due to {e}. Running a simulation as a demo.')
        try:
            RE(scan([det1], control, -1, 1, 100000))
        except Exception as e:
            print(f'This is the exception: {e}')
    return 'scanning'


@app.callback(
    Output('scan-img', 'figure'),
    Output('scan-output', 'columns'),
    Output('scan-output', 'data'),

    Input('scan-go', 'n_clicks'),
    Input('scan-abort', 'n_clicks'),
    Input('refresh-interval', 'n_intervals'),

    State('scan-cache', 'data'),
    prevent_initial_call=True
)
def manage_running_scan(scan_go, scan_abort, n_int, status):
    '''
    This callback starts a scan
    Args:
        scan_abort:     Abort button to stop a scan
        scan_cache:     Scan object
    Return:
        scan_output:    Scan output
    '''
    changed_id = dash.callback_context.triggered[0]['prop_id']
    results = dash.no_update
    columns = dash.no_update
    fig = dash.no_update
    if 'scan-abort' in changed_id:
        RE.abort()
    else:
        try:
            results = DB[-1].table()
            x = None
            y = None
            valid_columns = []
            for col in list(results.columns):
                comp = COMPONENT_LIST.find_component(name=col)
                if comp:
                    valid_columns.append(col)
                    if comp.type == ComponentType('control'):
                        x = col
                    elif comp.type == ComponentType('detector'):
                        y = col
            columns = [{'name': column, 'id': column} for column in list(valid_columns)]
            if x and y:
                fig = px.line(results, x=x, y=y)
                fig.update_layout( margin=dict(l=20, r=20, t=20, b=20))
            results = results.to_dict('records')
        except Exception as e:
            print(f'plot failed due to: {e}')
    return fig, columns, results


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
