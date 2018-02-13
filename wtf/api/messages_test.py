# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import messages
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_SENDER_ID = '0b0b0b0b-0b0b-0b0b-0b0b-0b0b0b0b0b0b'
TEST_SUBJECT = 'foo'
TEST_BODY = 'foobar'
TEST_RECIPIENTS = ['0c0c0c0c-0c0c-0c0c-0c0c-0c0c0c0c0c0c', '0d0d0d0d-0d0d-0d0d-0d0d-0d0d0d0d0d0d']


def setup_function():
    messages.REPO = {'by_id': {}}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/messages')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.messages.save')
@patch('wtf.api.messages.find_by_id')
def test_handle_create_message_request(
        mock_find_by_id,
        mock_save,
        test_client
    ):
    expected = 'foobar'
    mock_find_by_id.return_value = None
    mock_save.return_value = expected
    response = test_client.post(
        body={'body': TEST_BODY, 'subject': TEST_SUBJECT, 'recipients': TEST_RECIPIENTS}
    )
    response.assert_status_code(200)


def test_create_message_defaults():
    expected = {
        'id': None,
        'parent': None,
        'sender': None,
        'subject': '(No Subject)',
        'body': None,
        'copies': []
    }
    actual = messages.create()
    actual.pop('created_at')
    assert expected == actual
