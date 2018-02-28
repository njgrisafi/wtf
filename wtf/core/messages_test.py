# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest
from mock import patch
from wtf.core import messages
from wtf.core.errors import NotFoundError, ValidationError

TEST_DATA = {
    'id': '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d',
    'sender': '0b0b0b0b-0b0b-0b0b-0b0b-0b0b0b0b0b0b',
    'subject': 'foo',
    'body': 'foobar',
    'recipients': ['0c0c0c0c-0c0c-0c0c-0c0c-0c0c0c0c0c0c']
}


def setup_function():
    messages.REPO = {'by_id': {}, 'by_recipient': {}}


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


@patch('wtf.core.messages.uuid4')
@patch('wtf.core.messages.validate')
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
    assert [expected['copies'][0]] == messages.REPO['by_recipient']['foo']
    assert [expected['copies'][1]] == messages.REPO['by_recipient']['bar']


@patch('wtf.core.messages.validate')
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

@patch('wtf.core.messages.find_by_recipient')
def test_get_recipient_messages(mock_find_by_recipient):
    expected = ['foobar']
    messages.REPO['by_id'][TEST_DATA['id']] = expected[0]
    mock_find_by_recipient.return_value = [
        {'message': TEST_DATA['id'], 'status': 'unread'}
    ]
    actual = messages.get_recipient_messages()
    assert expected == actual


@patch('wtf.core.messages.find_by_recipient')
def test_get_recipient_messages_status(mock_find_by_recipient):
    expected = []
    status = 'unread'
    mock_find_by_recipient.return_value = [
        {'message': TEST_DATA['id'], 'status': 'read'}
    ]
    actual = messages.get_recipient_messages(status=status)
    assert expected == actual


def test_find_message_by_id():
    expected = 'foobar'
    messages.REPO['by_id'][TEST_DATA['id']] = expected
    actual = messages.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_message_by_id_not_found():
    expected = 'Message not found'
    with pytest.raises(NotFoundError) as e:
        messages.find_by_id(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual


def test_find_message_by_recipient():
    expected = 'foobar'
    messages.REPO['by_recipient'][TEST_DATA['id']] = expected
    actual = messages.find_by_recipient(TEST_DATA['id'])
    assert expected == actual


def test_find_message_by_recipient_not_found():
    expected = 'Recipient not found'
    with pytest.raises(NotFoundError) as e:
        messages.find_by_recipient(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual
