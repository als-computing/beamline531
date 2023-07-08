import json
import math
import os
import requests

BL_API_KEY = str(os.environ.get("BL_API_KEY"))
json_path = os.path.join("/app/work/src/epics_db", "epics_happi_db.json")
# json_path = "epics_happi_db.json"

assert os.path.exists(
    json_path
), f"JSON path: {json_path} not exist. Current directory: {os.path.abspath('.')}"

with open(json_path) as f:
    db_dict = json.load(f)
comp_list = []
for elem in db_dict.keys():
    sub_elem = db_dict[elem]
    comp = {}
    comp["name"] = elem
    if sub_elem["prefix"] is not None:
        comp["prefix"] = sub_elem["prefix"]
    else:
        comp["prefix"] = "not assigned"
    comp["active"] = bool(sub_elem["active"])
    comp["functional_group"] = sub_elem["functional_group"]
    comp["type"] = sub_elem["type"]
    comp["device_class"] = sub_elem["device_class"]
    comp["args"] = sub_elem["args"]
    if sub_elem["documentation"] is not None:
        comp["documentation"] = sub_elem["documentation"]
    if sub_elem["unit"] is not None:
        comp["unit"] = sub_elem["unit"]
    if sub_elem["z"] is not None and not math.isnan(sub_elem["z"]):
        comp["z"] = sub_elem["z"]
    if sub_elem["port"] is not None and sub_elem["port"] != "none":
        comp["port"] = sub_elem["port"]
    comp_list.append(comp)

beamline = {"name": "5.3.1", "components": comp_list}

status = requests.post(
    "http://beamline_api:8090/api/v0/beamline",
    json=beamline,
    headers={"api_key": BL_API_KEY},
)

print(status.json())
