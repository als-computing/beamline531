from fastapi.testclient import TestClient
from typing import List

from main import API_URL_PREFIX
from model import Beamline


def test_beamline(rest_client: TestClient):
    response = rest_client.post(f"{API_URL_PREFIX}/beamline", json=beamline1)
    assert response.status_code == 200
    beamline1_uid = response.json()['uid']

    response: Beamline = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline1_uid}")
    assert response.status_code == 200, f"error: {response.text}"
    beamline = response.json()
    
    source = response.json()
    assert source['uid'] == beamline1_uid
    
    response: List[Beamline] = rest_client.get(f"{API_URL_PREFIX}/beamlines")
    assert response.status_code == 200, f"error: {response.text}"
    beamlines = response.json()
    assert len(beamlines) == 1

    response = rest_client.patch(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", json={"add_components": [component2]})
    assert response.status_code == 200
    
    component1_uid = beamline['components'][0]['uid']
    response = rest_client.patch(f"{API_URL_PREFIX}/beamline/{beamline1_uid}", json={"remove_components": [component1_uid]})
    assert response.status_code == 200
    
    response: Beamline = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline1_uid}")
    assert len(response.json()['components']) == 1

    response: rest_client.delete(f"{API_URL_PREFIX}/beamline/{beamline1_uid}")
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

