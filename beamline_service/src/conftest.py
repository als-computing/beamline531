from fastapi.testclient import TestClient
import pytest
import mongomock

from src.main import app, set_beamline_service, set_auth_service
from src.beamline_service import BeamlineService
from src.api_auth_service import AuthService


@pytest.fixture(scope="module")
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture(scope="module")
def beamline_svc(mongodb):
    beamline_svc = BeamlineService(mongodb)
    return beamline_svc


@pytest.fixture(scope="module")
def auth_svc(mongodb):
    auth_svc = AuthService(mongodb)
    return auth_svc


@pytest.fixture(scope="module")
def rest_client(beamline_svc, auth_svc):
    set_beamline_service(beamline_svc)
    set_auth_service(auth_svc)
    auth_svc.create_api_client("user1", "client1", "api1")
    return TestClient(app)
