from fastapi.testclient import TestClient
import pytest
import mongomock

from api import app, set_component_service, svc_context
from component_service import ComponentService


@pytest.fixture(scope="module")
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture(scope="module")
def component_svc(mongodb):
    component_svc = ComponentService(mongodb)
    return component_svc


@pytest.fixture(scope="module")
def rest_client(component_svc):
    set_component_service(component_svc)
    return TestClient(app)
