import sys, json
from epicsdb import getClientPath, getCollection, create_dbApp

# Get configuration setting from a config file
assert (len(sys.argv) == 2), "Missing mongoDB config.json as the input argument"

# load config.json file
with open(sys.argv[1], 'r') as d:
    inputs = json.load(d)

# initiate MongoDB client and get db collection
clientpath = getClientPath(input_dic=inputs)
collection = getCollection(clientpath, inputs['DB'], inputs['COLLECTION'])

# create dash app and launch
app = create_dbApp(collection)
if __name__ == '__main__':
    app.run_server(debug=False)




