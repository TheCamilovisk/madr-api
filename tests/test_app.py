from http import HTTPStatus

from fastapi.testclient import TestClient

from madr_api.app import app

client = TestClient(app)


def test_root_must_return_ok_and_hello_world(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}
