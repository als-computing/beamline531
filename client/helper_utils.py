import logging

from json_editor import JSONParameterEditor


def load_bl_controls(controls_url):
    response = requests.get(controls_url)
    if response.status_code == 200:
        controls = response.json()
        gui_items = JSONParameterEditor(_id={'type': 'parameter_editor'},
                                        json_blob=parameters)
        gui_items.init_callbacks(app)
    else:
        logging.warning(f'Get request from controls api returned: {response.status_code}')
        gui_items = []
    return gui_items

