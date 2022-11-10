from fastapi.testclient import TestClient
import pytest
import mongomock

from api import app, set_control_service, svc_context
from control_service import ControlService


@pytest.fixture(scope="module")
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture(scope="module")
def control_svc(mongodb):
    control_svc = ControlService(mongodb)
    return control_svc


@pytest.fixture(scope="module")
def rest_client(control_svc):
    set_control_service(control_svc)
    return TestClient(app)
