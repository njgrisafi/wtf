# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from wtf.api.app import create_app
from wtf.testing import create_test_client


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/health')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


def test_handle_healthcheck_request(test_client):
    expected = b'Healthy'
    response = test_client.get()
    response.assert_status_code(200)
    response.assert_body(expected)
