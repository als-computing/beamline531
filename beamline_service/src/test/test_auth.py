
def test_key(auth_svc):
    auth_svc.create_api_client("user1", "client1", "api1")
    key = auth_svc.create_api_client("user1", "client1", "api2")
    api_client_key = auth_svc.verify_api_key(key)
    assert api_client_key.client == "client1"
    assert api_client_key.api == "api2"
    api_clients = auth_svc.get_api_clients("user1")
    sirius_keys = []
    [
        sirius_keys.append(key)
        for api_client in api_clients
        if api_client.client == "client1"
    ]
    assert len(sirius_keys) == 2


def test_non_existent_key(auth_svc):
    auth_svc.create_api_client("user1", "client1", "api1")
    auth_svc.create_api_client("user1", "client1", "api2")
    api_client_key = auth_svc.verify_api_key("foobar")
    assert api_client_key is None
    clients = auth_svc.get_api_clients("user1")
    assert len(clients) > 0

