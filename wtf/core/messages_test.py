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


def test_create_defaults():
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


def test_create_copy_defaults():
    expected = {
        'message': 'foo',
        'recipient': None,
        'status': 'unread',
        'timestamps': {
            'read_at': None,
            'deleted_at': None
        }
    }
    actual = messages.create_copy({'id': 'foo'})
    assert expected == actual


@patch('wtf.core.messages.create_copy')
def test_create_copies(mock_create_copy):
    expected = ['foo']
    mock_create_copy.return_value = 'foo'
    actual = messages.create_copies('foo', ['bar'])
    assert expected == actual


@patch('wtf.core.messages.uuid4')
@patch('wtf.core.messages.validate')
def test_save_message_insert(mock_validate, mock_uuid4):
    expected = {
        'id': TEST_DATA['id'],
        'parent': 'foo',
        'sender': None,
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body']
    }
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_DATA['id']
    actual = messages.save({
        'parent': 'foo',
        'sender': None,
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body']
    })
    assert expected == actual
    assert expected == messages.REPO['by_id'][TEST_DATA['id']]
    assert [expected] == messages.REPO['by_parent'][expected['parent']]


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


@patch('wtf.core.messages.save_copy')
def test_save_copies_insert(mock_save_copy):
    expected = ['foo', 'bar']
    actual = messages.save_copies(expected)
    assert expected == actual
    assert mock_save_copy.call_count == len(expected)


@patch('wtf.core.messages.validate_copy')
def test_save_copy_insert(mock_validate_copy):
    expected = {
        'timestamps': {
            'deleted_at': None,
            'read_at': None
        },
        'message': TEST_DATA['id'],
        'recipient': 'foo',
        'status': 'unread'
    }
    mock_validate_copy.return_value = None
    actual = messages.save_copy(expected)
    assert expected == actual
    assert [expected] == messages.REPO_COPIES['by_id'][TEST_DATA['id']]
    key = TEST_DATA['id'] + ',' + expected['recipient']
    assert expected == messages.REPO_COPIES['by_id_and_recipient'][key]
    assert [expected] == messages.REPO_COPIES['by_recipient'][expected['recipient']]


@patch('wtf.core.messages.validate_copy')
def test_save_copy_invalid(mock_validate_copy):
    mock_validate_copy.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        messages.save_copy({})
    assert not messages.REPO_COPIES['by_id'].values()
    assert not messages.REPO_COPIES['by_id_and_recipient'].values()
    assert not messages.REPO_COPIES['by_recipient'].values()


def test_validate():
    messages.validate({
        'id': TEST_DATA['id'],
        'parent': None,
        'sender': None,
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body'],
        'copies': []
    })


def test_validate_missing_fields():
    expected = [
        'Missing required field: subject',
        'Missing required field: body',
        'Missing required field: copies'
    ]
    with pytest.raises(ValidationError) as e:
        messages.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_copy():
    messages.validate_copy({
        'recipient': 'foo',
        'status': 'bar',
        'timestamps': 'foobar',
        'message': 'test'
    })


def test_validate_copy_missing_fields():
    expected = [
        'Missing required field: recipient',
        'Missing required field: status',
        'Missing required field: timestamps'
    ]
    with pytest.raises(ValidationError) as e:
        messages.validate_copy({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


@patch('wtf.core.messages.find_copies_by_recipient_id')
def test_get_recipient_message_copies(mock_find_copies_by_recipient_id):
    expected = [{'message': TEST_DATA['id'], 'status': 'unread'}]
    mock_find_copies_by_recipient_id.return_value = expected
    actual = messages.get_recipient_message_copies()
    assert expected == actual


@patch('wtf.core.messages.find_copies_by_recipient_id')
def test_get_recipient_message_copies_by_status(mock_find_copies_by_recipient_id):
    expected = []
    status = 'unread'
    mock_find_copies_by_recipient_id.return_value = [
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


def test_find_by_parent_id():
    expected = 'foobar'
    messages.REPO['by_parent'][TEST_DATA['id']] = expected
    actual = messages.find_by_parent_id(TEST_DATA['id'])
    assert expected == actual


def test_find_by_parent_id_not_found():
    expected = 'Parent messages not found'
    with pytest.raises(NotFoundError) as e:
        messages.find_by_parent_id(TEST_DATA['id'])
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


def test_find_copies_by_recipient_id():
    expected = 'foobar'
    messages.REPO_COPIES['by_recipient'][TEST_DATA['id']] = expected
    actual = messages.find_copies_by_recipient_id(TEST_DATA['id'])
    assert expected == actual


def test_find_copies_by_recipient_id_not_found():
    expected = 'Recipient not found'
    recipient = 'foo'
    with pytest.raises(NotFoundError) as e:
        messages.find_copies_by_recipient_id(recipient)
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
            'timestamps': {
                'deleted_at': None,
                'read_at': None
            },
            'message': TEST_DATA['id'],
            'recipient': 'foo',
            'status': 'unread'
        },
        {
            'timestamps': {
                'deleted_at': None,
                'read_at': None
            },
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


def test_transform_with_copies():
    message_copies = [
        {
            'timestamps': {
                'deleted_at': None,
                'read_at': None
            },
            'message': TEST_DATA['id'],
            'recipient': 'foo',
            'status': 'unread'
        },
        {
            'timestamps': {
                'deleted_at': None,
                'read_at': None
            },
            'message': TEST_DATA['id'],
            'recipient': 'bar',
            'status': 'unread'
        }
    ]
    expected = {
        'id': TEST_DATA['id'],
        'sender': TEST_DATA['sender'],
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body'],
        'copies': message_copies
    }
    actual = messages.transform({
        'id': TEST_DATA['id'],
        'sender': TEST_DATA['sender'],
        'subject': TEST_DATA['subject'],
        'body': TEST_DATA['body']
    }, message_copies=message_copies)
    assert expected == actual


@patch('wtf.core.messages.find_by_id')
def test_transform_copy(mock_find_by_id):
    expected = {
        'timestamps': {
            'deleted_at': None,
            'read_at': None
        },
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
            'timestamps': {
                'deleted_at': None,
                'read_at': None
            },
            'message': TEST_DATA['id'],
            'recipient': 'foo',
            'status': 'unread'
        }
    )
    assert expected == actual


@patch('wtf.core.messages.transform_copy')
def test_transform_copies(mock_transform_copy):
    expected = [{
        'timestamps': {
            'deleted_at': None,
            'read_at': None
        },
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
            'timestamps': {
                'deleted_at': None,
                'read_at': None
            },
            'message': TEST_DATA['id'],
            'recipient': 'foo',
            'status': 'unread'
        }
    ])
    assert expected == actual


@patch('wtf.core.messages.transform')
def test_transform_all(mock_transform):
    expected = [{'transformed': 'transformed'}, {'transformed': 'transformed'}]
    mock_transform.return_value = {'transformed': 'transformed'}
    actual = messages.transform_all([{'foo1': 'bar1'}, {'foo2': 'bar2'}])
    assert expected == actual
