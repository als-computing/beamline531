from fastapi.testclient import TestClient

from api import API_URL_PREFIX

from model import BasicComponent, ClientBeamline, ComponentType


def test_beamline(rest_client: TestClient):
    response = rest_client.post(API_URL_PREFIX + "/components", json=[component1])
    assert response.status_code == 200
    component1_uid = response.json()['uids'][0]

    response: BasicComponent = rest_client.get(f"{API_URL_PREFIX}/component/{component1_uid}")
    assert response.status_code == 200, f"oops {response.text}"
    
    source = response.json()
    assert source['uid'] == component1_uid
    
    response = rest_client.post(f"{API_URL_PREFIX}/components", json=[component2])
    assert response.status_code == 200
    component2_uid = response.json()['uids'][0]

    response: BasicComponent = rest_client.get(f"{API_URL_PREFIX}/component/{component2_uid}")
    assert response.status_code == 200, f"oops {response.text}"
    
    source = response.json()
    assert source['uid'] == component2_uid

    beamline1['components_uids'] = [component1_uid, component2_uid]
    response = rest_client.post(f"{API_URL_PREFIX}/beamlines", json=beamline1)
    assert response.status_code == 200
    beamline_uid = response.json()['uid']

    response: ClientBeamline = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline_uid}")
    assert response.status_code == 200, f"oops {response.text}"
    
    source = response.json()
    assert source['uid'] == beamline_uid



component1 = {
    "prefix": "component1", 
    "name": "test1", 
    "type": "control", 
    "id": "comp1", 
    "min": 0, 
    "max": 100, 
    "step": 1, 
    "units": '°'}


component2 = {
    "prefix": "component2", 
    "name": "test2", 
    "type": "control", 
    "id": "comp2", 
    "min": 0, 
    "max": 25, 
    "step": 1, 
    "units": 'mm'}


beamline1 = {
    "version": 1,
    "name": "beamline1"
}

