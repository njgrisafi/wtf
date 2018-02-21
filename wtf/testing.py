'''
wtf.testing

Application testing helpers.
'''
from json import loads as json_loads, dumps as json_dumps


def create_test_client(app):
    '''Create a test client from a Flask app'''
    app.testing = True
    client = TestClient(app.test_client())
    app.app_context()
    return client


class TestClient(object):
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

    def post(self, path='', **kwargs):
        '''Send a POST request'''
        path = '%s%s' % (self.root_path, path)
        headers = kwargs.get('headers', self.default_headers)
        body = kwargs.get('body')
        data = json_dumps(body) if body is not None else None
        response = self.test_client.post(
            path=path,
            headers=headers,
            data=data
        )
        return AssertableResponse(response)

    def get(self, path='', **kwargs):
        '''Send a GET request'''
        query_string = kwargs.get('query_string', {})
        path = '%s%s' % (self.root_path, kwargs.get('path', ''))
        headers = kwargs.get('headers', self.default_headers)
        response = self.test_client.get(
            path=path,
            headers=headers,
            query_string=query_string
        )
        return AssertableResponse(response)


class AssertableResponse(object):
    '''An assertion wrapper for Flask responses'''

    def __init__(self, response):
        self.response = response

    def assert_status_code(self, expected):
        '''Assert that the response status code is as expected'''
        actual = self.response.status_code
        message = 'Expected response status code to be %d, got %d'
        message %= (expected, actual)
        assert expected == actual, message

    def assert_body(self, expected):
        '''Assert that the response body is as expected'''
        actual = self.response.get_data()
        if self.response.content_type == 'application/json':
            actual = json_loads(actual)
        message = 'Expected response body to be %s, got %s'
        message %= (expected, actual)
        assert expected == actual, message
