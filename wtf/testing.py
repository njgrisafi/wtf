'''
wtf.testing

Testing helpers.
'''
import json


def create_test_client(app):
    '''Create a test client from a Flask app'''
    app.testing = True
    client = Client(app.test_client())
    app.app_context()
    return client


class Client(object):
    '''A convenience wrapper for Flask test clients'''

    test_client = None
    root_path = '/'
    default_headers = {}

    def __init__(self, test_client):
        self.test_client = test_client

    def set_root_path(self, path):
        '''Set the root request path'''
        self.root_path = path

    def set_default_headers(self, headers):
        '''Set the default request headers'''
        self.default_headers = headers

    def post(self, **kwargs):
        '''Send a POST request'''
        path = '%s%s' % (self.root_path, kwargs.get('path', ''))
        headers = kwargs.get('headers', self.default_headers)
        body = kwargs.get('body', None)
        data = json.dumps(body) if body else None
        response = self.test_client.post(
            path=path,
            headers=headers,
            data=data
        )
        return AssertableResponse(response)


class AssertableResponse(object):
    '''An assertion wrapper for Flask responses'''

    def __init__(self, response):
        self.response = response

    def assert_status_code(self, expected):
        '''Assert that the response status code is as expected'''
        assert self.response.status_code == expected

    def assert_body(self, expected):
        '''Assert that the response body is as expected'''
        assert json.loads(self.response.data) == expected
