# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import messages
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client

TEST_DATA = {
    'id': '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d',
    'sender': '0b0b0b0b-0b0b-0b0b-0b0b-0b0b0b0b0b0b',
    'subject': 'foo',
    'body': 'foobar',
    'recipients': ['0c0c0c0c-0c0c-0c0c-0c0c-0c0c0c0c0c0c']
}
# TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
# TEST_SENDER_ID = '0b0b0b0b-0b0b-0b0b-0b0b-0b0b0b0b0b0b'
# TEST_SUBJECT = 'foo'
# TEST_BODY = 'foobar'
# TEST_RECIPIENTS = ['0c0c0c0c-0c0c-0c0c-0c0c-0c0c0c0c0c0c', '0d0d0d0d-0d0d-0d0d-0d0d-0d0d0d0d0d0d']


def setup_function():
    messages.REPO = {'by_id': {}, 'by_recipient': {}}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/messages')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.messages.save')
def test_handle_create_message_request(
        mock_save,
        test_client
    ):
    expected = 'foobar'
    mock_save.return_value = expected
    response = test_client.post(
        body={'body': TEST_DATA['body'], 'subject': TEST_DATA['subject'], 'recipients': TEST_DATA['recipients']}
    )
    response.assert_status_code(200)
    response.assert_body({'message': 'foobar'})


@patch('wtf.api.messages.find_by_id')
def test_handle_get_by_id_request(
        mock_find_by_id,
        test_client
    ):
    expected = {'message': TEST_DATA}
    mock_find_by_id.return_value = TEST_DATA
    for _ in range(2):
        response = test_client.get(path='/%s' % TEST_DATA['id'])
        response.assert_status_code(200)
        response.assert_body(expected)


@patch('wtf.api.messages.find_by_recipient')
def test_handle_get_query_request(
        mock_find_by_recipient,
        test_client
    ):
    expected = 'foobar'
    mock_find_by_recipient.return_value = expected
    response = test_client.get(
        query_string={'recipient': TEST_DATA['recipients'][0]}
    )
    response.assert_status_code(200)
    response.assert_body({'messages': 'foobar'})


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


@patch('wtf.api.messages.uuid4')
@patch('wtf.api.messages.validate')
def test_save_message_insert(mock_validate, mock_uuid4):
    expected = {
        'id': TEST_DATA['id'],
        'parent': None,
        'sender': None,
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body'],
        'copies': [
            {
                'deleted_at': None,
                'read_at': None,
                'message': TEST_DATA['id'],
                'recipient': 'foo',
                'status': 'unread'
            },
            {
                'deleted_at': None,
                'read_at': None,
                'message': TEST_DATA['id'],
                'recipient': 'bar',
                'status': 'unread'
            }
        ]
    }
    test_message = expected.copy()
    test_message['id'] = None
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_DATA['id']
    actual = messages.save(test_message)
    assert expected == actual
    assert expected == messages.REPO['by_id'][TEST_DATA['id']]
    print(messages.REPO['by_recipient']['foo'])
    assert [expected] == messages.REPO['by_recipient']['foo']
    assert [expected] == messages.REPO['by_recipient']['bar']


@patch('wtf.api.messages.validate')
def test_save_message_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        messages.save({})
    assert not messages.REPO['by_id'].values()
    assert not messages.REPO['by_recipient'].values()


def test_validate_message():
    messages.validate({
        'id': TEST_DATA['id'],
        'parent': None,
        'sender': None,
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body'],
        'copies': []
    })


def test_validate_message_missing_fields():
    expected = [
        'Missing required field: subject',
        'Missing required field: body',
        'Missing required field: copies'
    ]
    with pytest.raises(ValidationError) as e:
        messages.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)
