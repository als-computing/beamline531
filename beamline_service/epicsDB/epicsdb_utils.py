
import dash, json, pymongo, happi
from dash import html, dcc, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
import bson.json_util as json_util
from datetime import datetime
from happi.backends.mongo_db import MongoBackend
from beamline_service.epicsDB.OphydDash import OphydDash

DEFAULT_EPICS_DB = './beamline_service/epicsDB/epicsHappi_DB.json'

def getListOphydDashItems(mongoConfig_path = None, json_path = None):
    """
    Get list of ophydDash items. If mongoConfig_path is given, it will 
    attempt to save the collection in JSON file. If mongoConfig_path is
    not given but json_path is defined, this JSON file will be loaded
    using Happi.Client JSON backend.

    Parameters
    ----------
    mongoConfig_path : str, optional
        path of mongo configuration file
    json_path : str, optional
        path of a JSON EPICs PV collection
    
    Returns
      ------
      list, list of ophyddash object 
    
    """
    if mongoConfig_path is not None:
        config_dic = getConfigs(fpath_config=mongoConfig_path)
        fname = saveCollectionToJson(config_dic=config_dic)
    elif json_path is not None:
        fname = json_path
    else:
        fname = DEFAULT_EPICS_DB
    
    try:
        client = happi.Client(path=fname)
        itemlist = client.all_items
        ophydash_list = [OphydDash(l) for l in itemlist]
        return ophydash_list
    except Exception as e:
        print('Could not get the item list due to %s'%e)
    # if mongoConfig_path is None:
    #     mongoConfig_path = '/home/bl531/bl531_gui/beamline531_gyl/beamline_service/epicsDB/config_test.json'

    # client = happiClientMongoDB(mongoConfig_path)
    # itemlist = client.all_items



def saveCollectionToJson(config_dic:'dict', fname:'str'=None):
    clientpath = getClientPath(input_dic=config_dic)
    collection = getCollection(clientpath, dbName=config_dic['db'], collectionName=config_dic['collection'])
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

def happiClientMongoDB(mongoConfig_path: 'str'):
    mongoConfig = getConfigs(mongoConfig_path)
    mg = MongoBackend(host=mongoConfig['host'], user=mongoConfig['user'], pw=mongoConfig['pw'], 
                    db=mongoConfig['db'], collection=mongoConfig['collection'])
    client = happi.Client(mg)
    return client

def getClientPath(input_dic = None, fpath_config = None):
    assert (any([input_dic is not None, fpath_config is not None])), "Require either input_dict or fpath_config"
    if input_dic is None:
        print('Loading inputs from JSON config file: %s'%fpath_config)
        with open(fpath_config, 'r') as d:
            input_dic = json.load(d)
    clientlink = "mongodb+srv://%s:%s@%s"%(input_dic['user'], input_dic['pw'], input_dic['host'])
    return clientlink

def getConfigs(fpath_config):
    with open(fpath_config, 'r') as d:
        inputs = json.load(d)
    return inputs

def connectMongo(clientPath):
    client = None
    try:
        client = pymongo.MongoClient(clientPath)
    except ConnectionFailure as e:
        print('Cannot connect to Mongo' + e)
    return client

def getCollection(clientPath, dbName, collectionName):
    try:
        client = connectMongo(clientPath)
        collection = client.get_database(dbName).get_collection(collectionName)
        return collection
    except:
        print('Having issue connecting to MongoDB server')

# push a list of entry into MongoDB
def pushData_list(clientPath, dbName, collectionName, pvlist):
    client = connectMongo(clientPath)
    collection = client.get_database(dbName).get_collection(collectionName)
    for v in pvlist:
        try:
            v.pop('_id')
            v.pop('kwargs')
        except:
            print('No such fields')

        id = collection.insert_one(v)
        print('Uploading %s'%(v['name']))

# push dictionary into MongoDB
def pushData_dict(clientPath, dbName, collectionName, pvlist):
    client = connectMongo(clientPath)
    collection = client.get_database(dbName).get_collection(collectionName)
    for _,v in pvlist.items():
        try:
            del v['kwargs']
            del v['_id']
        except:
            print('No such fields')

        id = collection.insert_one(v)
        print('Uploading %s'%(v['name']))

# get the latest database from cloud
def getDB(clientPath, dbName, collectionName):
    client = connectMongo(clientPath)
    collection = client.get_database(dbName).get_collection(collectionName)
    df = pd.DataFrame(list(collection.find()))
    return df


# create dash app interface
def create_dbApp(collection):
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


