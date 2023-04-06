import sys, json
import sys
sys.path.append('/home/bl531/bl531_gui/beamline531_gyl')

from beamline_service.epicsDB.epicsdb_utils import *

# Get configuration setting from a config file
assert (len(sys.argv) == 2), "Missing mongoDB config.json as the input argument"

# load config.json file
dbConfigs = getConfigs(sys.argv[1])

# initiate MongoDB client and get db collection
clientpath = getClientPath(input_dic=dbConfigs)
collection = getCollection(clientpath, dbConfigs['db'], dbConfigs['collection'])

# create dash app and launch
app = create_dbApp(collection)
if __name__ == '__main__':
    app.run_server(debug=False)




