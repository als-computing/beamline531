from fastapi.testclient import TestClient

from api import API_URL_PREFIX

from model import Control, FullBeamline


def test_beamline(rest_client: TestClient):
    response = rest_client.post(API_URL_PREFIX + "/controls", json=control1)
    assert response.status_code == 200
    control1_uid = response.json()['uid']

    response: Control = rest_client.get(f"{API_URL_PREFIX}/control/{control1_uid}")
    assert response.status_code == 200, f"oops {response.text}"
    
    source = response.json()
    assert source['uid'] == control1_uid
    
    response = rest_client.post(f"{API_URL_PREFIX}/controls", json=control2)
    assert response.status_code == 200
    control2_uid = response.json()['uid']

    response: Control = rest_client.get(f"{API_URL_PREFIX}/control/{control2_uid}")
    assert response.status_code == 200, f"oops {response.text}"
    
    source = response.json()
    assert source['uid'] == control2_uid

    beamline1['controls_uids'] = [control1_uid, control2_uid]
    response = rest_client.post(f"{API_URL_PREFIX}/beamlines", json=beamline1)
    assert response.status_code == 200
    beamline_uid = response.json()['uid']

    response: FullBeamline = rest_client.get(f"{API_URL_PREFIX}/beamline/{beamline_uid}")
    assert response.status_code == 200, f"oops {response.text}"
    
    source = response.json()
    assert source['uid'] == beamline_uid


control1 = {
    "pv_name": "control1",
    "name": "test1",
    "gui_comp": [
        {"comp_type": "slider",
         "name": "cont1_gui1",
         "title": "cont1_gui1",
         "param_key": "cont1_gui1",
        },
        {"comp_type": "radio",
         "name": "cont1_gui2",
         "title": "cont1_gui2",
         "param_key": "cont1_gui2",
         "options": ["option1", "option2"]
        }
    ]
}

control2 = {
    "pv_name": "control2",
    "name": "test2",
    "gui_comp": [
        {"comp_type": "slider",
         "name": "cont2_gui1",
         "title": "cont2_gui1",
         "param_key": "cont2_gui1",
        }
    ]
}

beamline1 = {
    "version": 1,
    "name": "beamline1"
}

