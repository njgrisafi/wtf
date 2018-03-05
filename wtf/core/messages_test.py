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
    messages.REPO = {'by_id': {}, 'by_parent': {}}
    messages.REPO_COPIES = {'by_id': {}, 'by_id_and_recipient': {}, 'by_recipient': {}}


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
        'parent': 'foo',
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
    copies = expected.pop('copies')
    actual = messages.save(test_message)
    assert expected == actual
    assert expected == messages.REPO['by_id'][TEST_DATA['id']]
    assert [expected] == messages.REPO['by_parent'][expected['parent']]
    assert copies == messages.REPO_COPIES['by_id'][TEST_DATA['id']]
    assert [copies[0]] == messages.REPO_COPIES['by_recipient']['foo']
    assert [copies[1]] == messages.REPO_COPIES['by_recipient']['bar']
    for c in copies:
        key = TEST_DATA['id'] + ',' + c['recipient']
        assert c == messages.REPO_COPIES['by_id_and_recipient'][key]
        assert [c] == messages.REPO_COPIES['by_recipient'][c['recipient']]


@patch('wtf.core.messages.validate')
def test_save_message_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        messages.save({})
    assert not messages.REPO['by_id'].values()
    assert not messages.REPO['by_parent'].values()
    assert not messages.REPO_COPIES['by_id'].values()
    assert not messages.REPO_COPIES['by_id_and_recipient'].values()
    assert not messages.REPO_COPIES['by_recipient'].values()


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


@patch('wtf.core.messages.find_copies_by_recipient')
def test_get_recipient_message_copies(mock_find_copies_by_recipient):
    expected = [{'message': TEST_DATA['id'], 'status': 'unread'}]
    mock_find_copies_by_recipient.return_value = expected
    actual = messages.get_recipient_message_copies()
    assert expected == actual


@patch('wtf.core.messages.find_copies_by_recipient')
def test_get_recipient_message_copies_by_status(mock_find_copies_by_recipient):
    expected = []
    status = 'unread'
    mock_find_copies_by_recipient.return_value = [
        {'message': TEST_DATA['id'], 'status': 'read'}
    ]
    actual = messages.get_recipient_message_copies(status=status)
    assert expected == actual


def test_find_by_id():
    expected = 'foobar'
    messages.REPO['by_id'][TEST_DATA['id']] = expected
    actual = messages.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_by_id_not_found():
    expected = 'Message not found'
    with pytest.raises(NotFoundError) as e:
        messages.find_by_id(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual


def test_find_by_parent():
    expected = 'foobar'
    messages.REPO['by_parent'][TEST_DATA['id']] = expected
    actual = messages.find_by_parent(TEST_DATA['id'])
    assert expected == actual


def test_find_by_parent_not_found():
    expected = 'Parent messages not found'
    with pytest.raises(NotFoundError) as e:
        messages.find_by_parent(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual



def test_find_copies_by_id():
    expected = 'foobar'
    messages.REPO_COPIES['by_id'][TEST_DATA['id']] = expected
    actual = messages.find_copies_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_copies_by_id_not_found():
    expected = 'Message copies not found'
    with pytest.raises(NotFoundError) as e:
        messages.find_copies_by_id(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual


def test_find_copies_by_recipient():
    expected = 'foobar'
    messages.REPO_COPIES['by_recipient'][TEST_DATA['id']] = expected
    actual = messages.find_copies_by_recipient(TEST_DATA['id'])
    assert expected == actual


def test_find_copies_by_recipient_not_found():
    expected = 'Recipient not found'
    recipient = 'foo'
    with pytest.raises(NotFoundError) as e:
        messages.find_copies_by_recipient(recipient)
    actual = str(e.value)
    assert expected == actual


def test_find_copies_by_id_and_recipient():
    expected = 'foobar'
    recipient = 'foo'
    key = TEST_DATA['id'] + ',' + recipient
    messages.REPO_COPIES['by_id_and_recipient'][key] = expected
    actual = messages.find_copies_by_id_and_recipient(
        message_id=TEST_DATA['id'], recipient=recipient
    )
    assert expected == actual


def test_find_copies_by_id_and_recipient_not_found():
    expected = 'Message for Recipient not found'
    recipient = 'foo'
    with pytest.raises(NotFoundError) as e:
        messages.find_copies_by_id_and_recipient(message_id=TEST_DATA['id'], recipient=recipient)
    actual = str(e.value)
    assert expected == actual


@patch('wtf.core.messages.find_copies_by_id')
def test_transform(mock_find_copies_by_id):
    copies = [
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
    mock_find_copies_by_id.return_value = copies
    expected = {
        'id': TEST_DATA['id'],
        'sender': TEST_DATA['sender'],
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body'],
        'copies': copies
    }
    actual = messages.transform({
        'id': TEST_DATA['id'],
        'sender': TEST_DATA['sender'],
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body']
    })
    assert expected == actual



@patch('wtf.core.messages.find_by_id')
def test_transform_copy(mock_find_by_id):
    expected = {
        'deleted_at': None,
        'read_at': None,
        'message': TEST_DATA['id'],
        'recipient': 'foo',
        'status': 'unread',
        'original': {
            'id': TEST_DATA['id'],
            'sender': TEST_DATA['sender'],
            'subject': TEST_DATA['subject'],
            'body': TEST_DATA['body']
        }
    }
    mock_find_by_id.return_value = expected['original']
    actual = messages.transform_copy(
        {
            'deleted_at': None,
            'read_at': None,
            'message': TEST_DATA['id'],
            'recipient': 'foo',
            'status': 'unread'
        }
    )
    assert expected == actual


@patch('wtf.core.messages.transform_copy')
def test_transform_copies(mock_transform_copy):
    expected = [{
        'deleted_at': None,
        'read_at': None,
        'message': TEST_DATA['id'],
        'recipient': 'foo',
        'status': 'unread',
        'original': {
            'id': TEST_DATA['id'],
            'sender': TEST_DATA['sender'],
            'subject': TEST_DATA['subject'],
            'body': TEST_DATA['body']
        }
    }]
    mock_transform_copy.return_value = expected[0]
    actual = messages.transform_copies([
        {
            'deleted_at': None,
            'read_at': None,
            'message': TEST_DATA['id'],
            'recipient': 'foo',
            'status': 'unread'
        }
    ])
    assert expected == actual
