# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import json


def assert_post(test_client, **kwargs):
    path = kwargs.get('path', '/')
    headers = kwargs.get('headers', {'Content-Type': 'application/json'})
    body = kwargs.get('body', None)
    response_body = kwargs.get('response_body', None)
    response_code = kwargs.get('response_code', 200)
    response = test_client.post(
        path,
        headers=headers,
        data=json.dumps(body) if body else None
    )
    assert json.loads(response.data) == response_body
    assert response.status_code == response_code
