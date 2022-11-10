import json
import requests

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

# from helper_utils import 
from app_layout import app


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
