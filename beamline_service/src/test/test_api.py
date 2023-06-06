from fastapi.testclient import TestClient
from typing import List

from src.main import API_URL_PREFIX, API_KEY_NAME, BEAMLINE_API
from src.model import Beamline


def test_beamline(rest_client: TestClient, auth_svc):
    key = auth_svc.create_api_client("user1", "client1", BEAMLINE_API)
    response = rest_client.post(f"{API_URL_PREFIX}/beamline", 
                                json=beamline1, 
                                headers={API_KEY_NAME: key})
    assert response.status_code == 200
    beamline1_uid = response.json()['uid']

    response: Beamline = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", 
                                         headers={API_KEY_NAME: key})
    assert response.status_code == 200, f"error: {response.text}"
    beamline = response.json()
    
    source = response.json()
    assert source['uid'] == beamline1_uid
    
    response: List[Beamline] = rest_client.get(f"{API_URL_PREFIX}/beamlines", 
                                               headers={API_KEY_NAME: key})
    assert response.status_code == 200, f"error: {response.text}"
    beamlines = response.json()
    assert len(beamlines) == 1

    response = rest_client.patch(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", 
                                 json={"add_components": [component2]}, 
                                 headers={API_KEY_NAME: key})
    assert response.status_code == 200
    
    component1_uid = beamline['components'][0]['uid']
    response = rest_client.patch(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", 
                                 json={"remove_components": [component1_uid]}, 
                                 headers={API_KEY_NAME: key})
    assert response.status_code == 200
    
    response: Beamline = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", 
                                         headers={API_KEY_NAME: key})
    assert len(response.json()['components']) == 1
    
    response = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline1_uid}/components", 
                               headers={API_KEY_NAME: key})
    assert len(response.json()) == 1

    response: rest_client.delete(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", 
                                 headers={API_KEY_NAME: key})
    assert response.status_code == 200

    
component1 = {
    "name": "name",
    "prefix": "prefix",
    "active": False,
    "device_class": "ophyd.EpicsMotor",
    }


component2 = {
    "name": "name",
    "prefix": "prefix",
    "active": True,
    "device_class": "ophyd.EpicsMotor",
    }


beamline1 = {
    "name": "beamline1",
    "qserver": {"url": "https://localhost", "api_key": "dummy_key"},
    "components": [component1]
    }

