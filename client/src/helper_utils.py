import pandas as pd

from src.model import ComponentType


def comp_list_to_options(comp_list):
    '''
    Converts a list of ophyd components to dash dropwdon options
    Args:
        comp_list:      List of ophyd components
    Returns:
        options:        Dash dropdown options with name and component id
    '''
    options=[]
    for component in comp_list:
        options.append({'label': component.name, 'value': component.id})
    return options


def add2table_remove_from_dropdown(component_list, dropdown_options, data_table, comp_id):
    '''
    Adds new component to scan table and removes this component from it's corresponding dropdown
    Args:
        component_list:     List of components at beamline
        dropdown_options:   Dropdown options for detectors/controls
        data_table:         Details within scan table
        comp_id:            Component ID to add to scan table
    Returns:
        data_table:         Updated table with the component to add
        dropdown_options:   Updated dropdown where the component added to the table is removed
                            from the dropdown
    '''
    component = component_list.find_component(comp_id)
    if component:
        data_table.append(
            {
                'prefix': component.prefix,
                'name': component.name,
                'type': component.type,
                'id': component.id,
                'start': component.min,
                'stop': component.max
            }
        )
    dropdown_options.remove({'label': component.name, 'value': component.id})
    return data_table, dropdown_options



def add2dropdown(component_list, control_options, detector_options, data_table, data_table_prev):
    '''
    
    '''
    if len(data_table)==0:
        component = component_list.find_component(data_table_prev[0]['id'])
    else:
        pd_table = pd.DataFrame.from_records(data_table)
        for component in data_table_prev:
            if component['id'] not in list(pd_table['id']):
                component = component_list.find_component(component['id'])
                break
    if component.type == ComponentType('control'):
        control_options = control_options + comp_list_to_options([component])
    else:
        detector_options = detector_options + comp_list_to_options([component])
    return control_options, detector_options

