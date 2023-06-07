from bson.objectid import ObjectId
import bson.json_util as json_util
import logging
from datetime import datetime
import json

import dash
from dash import html, dcc, Input, Output, State, dash_table
import happi
from happi.backends.mongo_db import MongoBackend
import pandas as pd
import plotly.express as px
import pymongo
from pymongo.errors import ConnectionFailure

from src.epics_db.ophyd_dash import OphydDash
from src.epics_db.model import RawJSONClient


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

DEFAULT_EPICS_DB = './beamline_service/epicsDB/epicsHappi_DB.json'


def get_ophyd_dash_items(mongo_config_path = None, json_path = None, \
                         raw_json = None):
    """
    Get list of OphydDash items. If mongo_config_path is given, it will 
    attempt to save the collection in JSON file. If mongo_config_path is
    not given but json_path is defined, this JSON file will be loaded
    using Happi Client JSON backend. If raw_json is defined, the custom
    RawJSONClient will be used to load the components from the db.

    Parameters
    ----------
    mongo_config_path : str, optional
        path of mongo configuration file
    json_path : str, optional
        path of a JSON EPICs PV collection
    raw_json : str, optional
        raw JSON db content
    Returns
      ------
      list, list of OphydDash object 
    
    """
    try:
        if mongo_config_path is not None:
            client = happi_client_mongo_db(mongo_config_path)
        elif json_path is not None:
            client = happi.Client(path=json_path)
        elif raw_json is not None:
            ## Mongo to happi dict
            happi_dict = {}
            for elem in raw_json:
                happi_dict[elem['name']]: elem
            client = RawJSONClient(raw_json=happi_dict)
        else:
            client = happi.Client(path=DEFAULT_EPICS_DB)
        itemlist = client.all_items
        ophydash_list = [OphydDash(l) for l in itemlist]
        return ophydash_list
    except Exception as e:
        logging.error('Could not get the item list due to %s'%e)
    pass


def save_collection_to_json(config_dic:'dict', fname:'str'=None):
    client_path = get_client_path(input_dic=config_dic)
    collection = get_collection(client_path, db_name=config_dic['db'], \
                                collection_name=config_dic['collection'])
    df = pd.DataFrame(list(collection.find()))
    dflist = df.to_dict('records')
    json_dic = {d['name']:d for d in dflist}
    if fname is None:
        now = datetime.now()
        dt_string = now.strftime("%a %b %d %Y %H:%W:%S")
        fname = './beamline_service/epicsDB/temp/pvdb_%s.json'%dt_string
    with open(fname, 'w') as f:
        f.write(json_util.dumps(json_dic))
    return fname


def happi_client_mongo_db(mongo_config_path: 'str'):
    mongo_config = get_configs(mongo_config_path)
    mg = MongoBackend(host=mongo_config['host'], user=mongo_config['user'], \
                      pw=mongo_config['pw'], 
                    db=mongo_config['db'], collection=mongo_config['collection'])
    client = happi.Client(mg)
    return client


def get_client_path(input_dic = None, fpath_config = None):
    assert (any([input_dic is not None, fpath_config is not None])), \
        "Require either input_dict or fpath_config"
    if input_dic is None:
        logging.info('Loading inputs from JSON config file: %s'%fpath_config)
        with open(fpath_config, 'r') as d:
            input_dic = json.load(d)
    clientlink = "mongodb+srv://%s:%s@%s"%(input_dic['user'], input_dic['pw'], \
                                           input_dic['host'])
    return clientlink


def get_configs(fpath_config):
    with open(fpath_config, 'r') as d:
        inputs = json.load(d)
    return inputs


def connect_mongo(client_path):
    client = None
    try:
        client = pymongo.MongoClient(client_path)
    except ConnectionFailure as e:
        logging.error('Cannot connect to Mongo' + e)
    return client


def get_collection(client_path, db_name, collection_name):
    try:
        client = connect_mongo(client_path)
        collection = client.get_database(db_name).get_collection(collection_name)
        return collection
    except Exception as e:
        logging.error(f'Having issue connecting to MongoDB server. Error: {e}')
    pass


# push a list of entry into MongoDB
def push_data_list(client_path, db_name, collection_name, pv_list):
    client = connect_mongo(client_path)
    collection = client.get_database(db_name).get_collection(collection_name)
    for v in pv_list:
        try:
            v.pop('_id')
            v.pop('kwargs')
        except Exception as e:
            logging.error(f'No such fields {e}')
        id = collection.insert_one(v)
        logging.info('Uploading %s'%(v['name']))
    pass


# push dictionary into MongoDB
def push_data_dict(client_path, db_name, collection_name, pv_list):
    client = connect_mongo(client_path)
    collection = client.get_database(db_name).get_collection(collection_name)
    for _,v in pv_list.items():
        try:
            del v['kwargs']
            del v['_id']
        except Exception as e:
            logging.error(f'No such fields {e}')
        id = collection.insert_one(v)
        logging.info('Uploading %s'%(v['name']))
    pass


# get the latest database from cloud
def get_db(client_path, db_name, collection_name):
    client = connect_mongo(client_path)
    collection = client.get_database(db_name).get_collection(collection_name)
    df = pd.DataFrame(list(collection.find()))
    return df


# create dash app interface
def create_db_app(collection):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                    suppress_callback_exceptions=True)

    app.layout = html.Div([
        html.H1('EPICS Database', style={'textAlign': 'Center'}),
        # interval activated once/week or when page refreshed
        dcc.Interval(id='interval_db', interval=86400000 * 7, n_intervals=0),
        html.Div(id='mongo-datatable', children=[]),

        html.Div([
            html.Div(id='pie-graph', className='five columns'),
            html.Div(id='hist-graph', className='six columns'),
        ], className='row'),
        dcc.Store(id='changed-cell')
    ])

    # Display Datatable with data from Mongo database
    @app.callback(Output('mongo-datatable', component_property='children'),
                Input('interval_db', component_property='n_intervals')
                )
    def populate_datatable(n_intervals):
        # Convert the Collection (table) date to a pandas DataFrame
        df = pd.DataFrame(list(collection.find()))
        # Convert id from ObjectId to string so it can be read by DataTable
        df['_id'] = df['_id'].astype(str)

        return [
            dash_table.DataTable(
                id='our-table',
                data=df.to_dict('records'),
                # columns=[{'id':p, 'name':p, 'editable':True} for p in df if p!='_id']
                columns=[{'id': p, 'name': p, 'editable': False} if p == '_id'
                        else {'id': p, 'name': p, 'editable': True}
                        for p in df],
            ),
        ]

    # store the row id and column id of the cell that was updated
    app.clientside_callback(
        """
        function (input,oldinput) {
            if (oldinput != null) {
                if(JSON.stringify(input) != JSON.stringify(oldinput)) {
                    for (i in Object.keys(input)) {
                        newArray = Object.values(input[i])
                        oldArray = Object.values(oldinput[i])
                        if (JSON.stringify(newArray) != JSON.stringify(oldArray)) {
                            entNew = Object.entries(input[i])
                            entOld = Object.entries(oldinput[i])
                            for (const j in entNew) {
                                if (entNew[j][1] != entOld[j][1]) {
                                    changeRef = [i, entNew[j][0]] 
                                    break        
                                }
                            }
                        }
                    }
                }
                return changeRef
            }
        }    
        """,
        Output('changed-cell', 'data'),
        Input('our-table', 'data'),
        State('our-table', 'data_previous')
    )

    # Update MongoDB and create the graphs
    @app.callback(
        Output("pie-graph", "children"),
        Output("hist-graph", "children"),
        Input("changed-cell", "data"),
        Input("our-table", "data"),
    )
    def update_d(cc, tabledata):
        if cc is None:
            # Build the Plots
            pie_fig = px.pie(tabledata, values='quantity', names='day')
            hist_fig = px.histogram(tabledata, x='department', y='quantity')
        else:
            # print(f'changed cell: {cc}')
            # print(f'Current DataTable: {tabledata}')
            
            x = int(cc[0])
        

            # update the external MongoDB
            row_id = tabledata[x]['_id']
            col_id = cc[1]
            new_cell_data = tabledata[x][col_id]
            collection.update_one({'_id': ObjectId(row_id)},
                                    {"$set": {col_id: new_cell_data}})

            lastedit_col_id = list(tabledata[x].keys()).index('last_edit')
            print('In here after lastedit id')
            now = datetime.now()
            dt_string = now.strftime("%a %b %d %Y %H:%W:%S")
            print(dt_string)
            collection.update_one({'_id': ObjectId(row_id)},
                                    {"$set": {'last_edit': dt_string}})
            # Operations guide - https://docs.mongodb.com/manual/crud/#update-operations

            # pie_fig = px.pie(tabledata, values='quantity', names='day')
            # hist_fig = px.histogram(tabledata, x='department', y='quantity')

        return dcc.Graph(figure=pie_fig), dcc.Graph(figure=hist_fig)
    return app


