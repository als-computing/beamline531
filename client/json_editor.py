import json
import re

from dash import Dash, dcc, html, Input, Output, State, ALL
from dash._utils import create_callback_id
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_daq as daq
from dataclasses import dataclass
from typing import Union, Callable


app = None
_targeted_callbacks = []


@dataclass
class Callback:
    input: Input
    output: Output
    callable: Callable


class SimpleItem(dbc.FormGroup):
    def __init__(self,
                 name,
                 base_id,
                 title=None,
                 param_key=None,
                 type='number',
                 debounce=True,
                 **kwargs):
        self.name = name
        self.label = dbc.Label(title or name)
        self.input = dbc.Input(type=type,
                               debounce=debounce,
                               id={**base_id,
                                   'name': name,
                                   'param_key': param_key},
                               **kwargs)

        super(SimpleItem, self).__init__(children=[self.label, self.input])


class FloatItem(SimpleItem):
    pass


class IntItem(SimpleItem):
    def __init__(self, *args, **kwargs):
        if 'min' not in kwargs:
            kwargs['min'] = -9007199254740991
        super(IntItem, self).__init__(*args, step=1, **kwargs)


class StrItem(SimpleItem):
    def __init__(self, *args, **kwargs):
        super(StrItem, self).__init__(*args, type='text', **kwargs)


class SliderItem(dbc.FormGroup):
    def __init__(self,
                 name,
                 base_id,
                 title=None,
                 param_key=None,
                 debounce=True,
                 visible=True,
                 **kwargs):
        self.label = dbc.Label(title or name)
        self.input = dcc.Slider(id={**base_id,
                                    'name': name,
                                    'param_key': param_key,
                                    'layer': 'input'},
                                tooltip={"placement": "bottom", "always_visible": True},
                                **kwargs)

        style = {}
        if not visible:
            style['display'] = 'none'

        super(SliderItem, self).__init__(id={**base_id,
                                             'name': name,
                                             'param_key': param_key,
                                             'layer': 'form_group'},
                                         children=[self.label, self.input],
                                         style=style)


class DropdownItem(dbc.FormGroup):
    def __init__(self,
                 name,
                 base_id,  # shared by all components
                 title=None,
                 param_key=None,
                 debounce=True,
                 visible=True,
                 **kwargs):
        self.label = dbc.Label(title or name)
        self.input = dcc.Dropdown(id={**base_id,
                                      'name': name,
                                      'param_key': param_key,
                                      'layer': 'input'},
                                  **kwargs)

        style = {}
        if not visible:
            style['display'] = 'none'

        super(DropdownItem, self).__init__(id={**base_id,
                                               'name': name,
                                               'param_key': param_key,
                                               'layer': 'form_group'},
                                           children=[self.label, self.input],
                                           style=style)


class RadioItem(dbc.FormGroup):
    def __init__(self,
                 name,
                 base_id,
                 title=None,
                 param_key=None,
                 visible=True,
                 **kwargs):
        self.label = dbc.Label(title or name)
        self.input = dbc.RadioItems(id={**base_id,
                                        'name': name,
                                        'param_key': param_key,
                                        'layer': 'input'},
                                    **kwargs)

        style = {}
        if not visible:
            style['display'] = 'none'

        super(RadioItem, self).__init__(id={**base_id,
                                            'name': name,
                                            'param_key': param_key,
                                            'layer': 'form_group'},
                                        children=[self.label, self.input],
                                        style=style)


class BoolItem(dbc.FormGroup):
    def __init__(self,
                 name,
                 base_id,
                 title=None,
                 param_key=None,
                 visible=True,
                 **kwargs):
        self.label = dbc.Label(title or name)
        self.input = daq.ToggleSwitch(id={**base_id,
                                          'name': name,
                                          'param_key': param_key,
                                          'layer': 'input'},
                                      **kwargs)
        self.output_label = dbc.Label('False/True')

        style = {}
        if not visible:
            style['display'] = 'none'

        super(BoolItem, self).__init__(id={**base_id,
                                           'name': name,
                                           'param_key': param_key,
                                           'layer': 'form_group'},
                                       children=[self.label, self.input, self.output_label],
                                       style=style)


class JSONParameterEditor(dbc.Form):
    type_map = {'float': FloatItem,
                'int': IntItem,
                'str': StrItem,
                'slider': SliderItem,
                'dropdown': DropdownItem,
                'radio': RadioItem,
                'bool': BoolItem,
                }

    def __init__(self, _id, json_blob, **kwargs):
        super(ParameterEditor, self).__init__(id=_id, children=[], className='kwarg-editor', **kwargs)
        self._json_blob = json_blob
        self.children = self.build_children()
    
    def init_callbacks(self, app):
        targeted_callback(self.stash_value,
                          Input({**self.id,
                                 'name': ALL},
                                'value'),
                          Output(self.id, 'n_submit'),
                          State(self.id, 'n_submit'),
                          app=app)
    
    def stash_value(self, value):
        # find the changed item name from regex
        r = '(?<=\"name\"\:\")[\w\-_]+(?=\")'
        matches = re.findall(r, dash.callback_context.triggered[0]['prop_id'])

        if not matches:
            raise LookupError('Could not find changed item name. Check that all parameter names use simple chars (\\w)')

        name = matches[0]
        self.parameters[name]['value'] = value
        return next(iter(dash.callback_context.states.values())) or 0 + 1

    @property
    def values(self):
        return {param['name']: param.get('value', None) for param in self._parameters}

    @property
    def parameters(self):
        return {param['name']: param for param in self._parameters}
    
    def _determine_type(self, parameter_dict):
        if 'type' in parameter_dict:
            if parameter_dict['type'] in self.type_map:
                return parameter_dict['type']
            elif parameter_dict['type'].__name__ in self.type_map:
                return parameter_dict['type'].__name__
        elif type(parameter_dict['value']) in self.type_map:
            return type(parameter_dict['value'])
        raise TypeError(f'No item type could be determined for this parameter: {parameter_dict}')

    def build_children(self, values=None):
        children = []
        for json_record in self._json_blob:
            ...
            # build a parameter dict from self.json_blob
            ...
            type = json_record.get('type', self._determine_type(json_record))
            json_record = json_record.copy()
            if values and json_record['name'] in values:
                json_record['value'] = values[json_record['name']]
            json_record.pop('type', None)
            item = self.type_map[type](**json_record, base_id=self.id)
            children.append(item)
        return children


def _dispatcher(*_):
    triggered = dash.callback_context.triggered
    if not triggered:
        raise PreventUpdate

    for callback in _targeted_callbacks:
        _id, _property = triggered[0]['prop_id'].split('.')
        if '{' in _id:
            _id = json.loads(_id)
        _input = Input(_id, _property)
        _id, _property = dash.callback_context.outputs_list.values()
        _output = Output(_id, _property)
        if callback.input == _input and callback.output == _output:
            return_value = callback.callable(triggered[0]['value'])
            if return_value is None:
                warnings.warn(
                    f'A callback returned None. Perhaps you forgot a return value? Callback: {repr(callback.callable)}')
            return return_value


def targeted_callback(callback, input: Input, output: Output, *states: State, app=app, prevent_initial_call=None):
    if prevent_initial_call is None:
        prevent_initial_call = app.config.prevent_initial_callbacks

    callback_id = create_callback_id(output)
    if callback_id in app.callback_map:
        if app.callback_map[callback_id]["callback"].__name__ != '_dispatcher':
            raise ValueError('Attempting to use a targeted callback with an output already assigned to a'
                             'standard callback. These are not compatible.')

        for callback_spec in app._callback_list:
            if callback_spec['output'] == callback_id:
                if callback_spec['prevent_initial_call'] != prevent_initial_call:
                    raise ValueError('A callback has already been registered to this output with a conflicting value'
                                     'for prevent_initial_callback. You should decide which you want.')
                callback_spec['inputs'].append(input.to_dict())
                callback_spec['state'].extend([state.to_dict() for state in states])
    else:
        app.callback(output, input, *states, prevent_initial_call=prevent_initial_call)(_dispatcher)

    _targeted_callbacks.append(Callback(input, output, callback))
