import logging
import os

import dash
from dash import Dash, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
import requests


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class BeamlineNotFound(Exception):
    pass


#### SETUP DASH APP ####
external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/style.css", 
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, assets_folder='../assets')
server = app.server
app.title = "BL 5.3.1 Manager"
app._favicon = 'LBL_icon.ico'

BL_API_URL = str(os.environ.get('BL_API_URL'))
BL_API_KEY = str(os.environ.get('BL_API_KEY'))
BL_UID = str(os.environ.get('BL_UID'))


def get_beamline():
    '''
    Get beamline information from database
    '''
    response = requests.get(f'{BL_API_URL}/beamline/{BL_UID}', headers={"api_key": BL_API_KEY})
    if response.status_code != 200:
        raise BeamlineNotFound(f'Status code: {response.status_code}')
    beamline = response.json()
    beamline_comps = beamline['components']
    df_beamline = pd.DataFrame(beamline_comps)
    df_beamline = df_beamline.drop(columns=['args'])
    return beamline.pop('components'), df_beamline


def update_beamline(modify_components=[], add_components=[], remove_components=[]):
    '''
    Update beamline information in dababase
    '''
    response = requests.patch(f"{BL_API_URL}/beamline/{BL_UID}", 
                              json={"modify_components": modify_components,
                                    "add_components": add_components,
                                    "remove_components": remove_components}, 
                              headers={"api_key": BL_API_KEY})
    return response

# Get init information to display
beamline_info, df_beamline = get_beamline()

### BEGIN DASH CODE ###
# APP HEADER
header = dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col(
                        html.Img(id="app-logo",
                                 src="../assets/LBL_logo.png",
                                 height="60px"),
                        md="auto"
                    ),
                    dbc.Col(
                        html.Div(
                            id = 'app-title',
                            children=[html.H3("Advanced Light Source | Beamline 5.3.1 Manager")],
                        ),
                        md=True,
                        align="center",
                    )
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.NavbarToggler(id="navbar-toggler"),
                        html.Div(
                            dbc.Nav([
                                dbc.NavItem(
                                    dbc.Button(className="fa fa-github",
                                               style={"font-size": 40, "margin-right": "1rem", "color": "#00313C", "background-color": "white"},
                                               href="https://github.com/als-computing/beamline531")
                                               ),
                                dbc.NavItem(
                                    dbc.Button(className="fa fa-question-circle-o",
                                               style={"font-size": 40, "color": "#00313C", "background-color": "white"},
                                               href="https://github.com/als-computing/beamline531")
                                               )
                            ],
                            navbar=True)
                        )
                    ])
                ])
            ],
            fluid=True),
        dark=True,
        color="#00313C",
        sticky="top"
        )

## CONTENTS
contents = dbc.Card([
                dbc.Row([
                    dbc.Button('Update database',
                               id='update-db',
                               color='success',
                               style={'width': '30%', 'margin-bottom': '1rem'}),
                    dbc.Button('Update table',
                               id='update-table',
                               color='success',
                               style={'width': '30%', 'margin-bottom': '1rem'})
                ]),
                dbc.Row([
                    dash_table.DataTable(
                        id='comp-table',
                        data=[],
                        columns=[{'id': p, 'name': p, 'editable': False} if p in ['creation', 'last_edit']
                                else {'id': p, 'name': p, 'editable': True}
                                for p in df_beamline.columns],
                        hidden_columns=['uid', 'schema_version'],
                        css=[{"selector": ".show-hide", "rule": "display: none"}],
                        style_header={'position': 'sticky', 'top': 0},
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        style_cell={'padding': '1rem',
                                    'textAlign': 'left',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'font-size': '15px',
                                    'maxWidth': 0},
                        style_table={
                            'overflowY': 'auto',
                            'width':'100%',
                            'height': '40%'
                            }
                    ),
                    dbc.Modal([
                        dbc.ModalHeader("Message"),
                        dbc.ModalBody(id="message-pop-up"),
                        dbc.ModalFooter([
                            dbc.Button(
                                "OK", 
                                id="ok-button", 
                                outline=False,
                                className="ms-auto", 
                                n_clicks=0
                            ),
                        ]),
                    ],
                    id="message-modal",
                    is_open=False,
                    ),
                ]),
            ],
            # fluid=True
        )

## LAYOUT
app.layout = html.Div(
    [
        header,
        contents
    ])

## CALLBACKS
@app.callback(
    Output('comp-table', 'data'),
    Output('message-pop-up', 'children'),
    Output('message-modal', 'is_open'),

    Input('update-db', 'n_clicks'),
    Input('update-table', 'n_clicks'),

    State('message-modal', 'is_open'),
    State('comp-table', 'data')
)
def update_database(update_db, update_table, is_open, table_data):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    table_data = pd.DataFrame.from_records(table_data)
    _ , df_bl_comps = get_beamline()
    if "update-db" in changed_id:
        if not df_bl_comps.equals(table_data):
            add_components = table_data.loc[table_data['uid']==None].to_dict('records')
            modify_components = []
            remove_components = []
            table_data = table_data.loc[table_data['uid']!=None]    # remove new components
            db_list_uids = df_bl_comps['uid'].tolist()
            current_list_uids = table_data['uid'].tolist()
            for uid in db_list_uids:
                if uid not in current_list_uids:                    # component was removed
                    remove_components.append(table_data.loc[df_beamline['uid']==uid])
                elif not table_data.loc[df_beamline['uid']==uid].equals(df_bl_comps.loc[df_bl_comps['uid']==uid]):
                    modify_components.append(table_data[table_data['uid']==uid].to_dict('records')[0])
            response = update_beamline(modify_components, add_components, remove_components)
            if response.status_code == 200:
                msg_info = 'The database has been updated'
            else:
                msg_info = f'The database was not updated due to {response.status_code}:{response.json()}'
            return dash.no_update, msg_info, not is_open
        else:
            return dash.no_update, dash.no_update, dash.no_update
    comp_list = df_bl_comps.to_dict('records')
    return comp_list, dash.no_update, dash.no_update


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
