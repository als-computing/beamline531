from fastapi.testclient import TestClient
import pytest
import mongomock

from main import app, set_beamline_service, svc_context
from beamline_service import BeamlineService


@pytest.fixture(scope="module")
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture(scope="module")
def beamline_svc(mongodb):
    beamline_svc = BeamlineService(mongodb)
    return beamline_svc


@pytest.fixture(scope="module")
def rest_client(beamline_svc):
    set_beamline_service(beamline_svc)
    return TestClient(app)
