# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import accounts
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


TEST_DATA = {
    'id': '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d',
    'email': 'foobar@gmail.com',
    'password': {
        'plain': 'foobar123',
        'hash': (
            'eb25d108f85572f28f1bc03f0fe08c557bddb5063d886bdab5acc9b2f6d07603'
            + '943ce08a96ebef2c71b71056e1992749304d5aeffd43bef476a77944f91624d3'
        )
    }
}


def setup_function():
    accounts.REPO = {'by_id': {}, 'by_email': {}}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/accounts')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.accounts.save')
def test_handle_post_account_request(mock_save, test_client):
    mock_save.return_value = 'foobar'
    response = test_client.post(body={})
    response.assert_status_code(201)
    response.assert_body({'account': 'foobar'})


@patch('wtf.api.accounts.save')
def test_handle_post_account_request_invalid(mock_save, test_client):
    mock_save.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post(body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.api.accounts.find_by_id')
def test_handle_get_account_by_id_request(mock_find_by_id, test_client):
    mock_find_by_id.return_value = {'foo': 'bar', 'password': 'foobar'}
    for _ in range(2):
        response = test_client.get(path='/%s' % TEST_DATA['id'])
        response.assert_status_code(200)
        response.assert_body({'account': {'foo': 'bar'}})


def test_handle_get_account_by_id_request_not_found(test_client):
    response = test_client.get(path='/%s' % TEST_DATA['id'])
    response.assert_status_code(404)
    response.assert_body({'errors': ['Account not found']})


@patch('wtf.api.accounts.util.salt_and_hash')
def test_create_account(mock_salt_and_hash):
    expected = {
        'id': TEST_DATA['id'],
        'email': TEST_DATA['email'],
        'password': TEST_DATA['password']['hash']
    }
    mock_salt_and_hash.return_value = TEST_DATA['password']['hash']
    actual = accounts.create(
        id=TEST_DATA['id'],
        email=TEST_DATA['email'],
        password=TEST_DATA['password']['hash']
    )
    assert expected == actual


def test_create_account_defaults():
    expected = {
        'id': None,
        'email': None,
        'password': None
    }
    actual = accounts.create()
    assert expected == actual


@patch('wtf.api.accounts.uuid4')
@patch('wtf.api.accounts.validate')
def test_save_account_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_DATA['id'], 'email': TEST_DATA['email']}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_DATA['id']
    actual = accounts.save({'id': None, 'email': TEST_DATA['email']})
    assert expected == actual
    assert expected == accounts.REPO['by_id'][TEST_DATA['id']]
    assert expected == accounts.REPO['by_email'][TEST_DATA['email']]


@patch('wtf.api.accounts.validate')
def test_save_account_update(mock_validate):
    expected = {'id': TEST_DATA['id'], 'email': TEST_DATA['email']}
    mock_validate.return_value = None
    actual = accounts.save({'id': TEST_DATA['id'], 'email': TEST_DATA['email']})
    assert expected == actual
    assert expected == accounts.REPO['by_id'][TEST_DATA['id']]
    assert expected == accounts.REPO['by_email'][TEST_DATA['email']]


@patch('wtf.api.accounts.validate')
def test_save_account_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        accounts.save({})
    assert not accounts.REPO['by_id'].values()
    assert not accounts.REPO['by_email'].values()


@patch('wtf.api.accounts.find_by_email')
def test_validate_account(mock_find_by_email):
    mock_find_by_email.side_effect = NotFoundError('foo bar baz')
    accounts.validate({
        'id': TEST_DATA['id'],
        'email': TEST_DATA['email'],
        'password': TEST_DATA['password']['plain']
    })


def test_validate_account_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: email',
        'Missing required field: password'
    ]
    with pytest.raises(ValidationError) as e:
        accounts.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


@patch('wtf.api.accounts.find_by_email')
def test_validate_account_email_already_registered(mock_find_by_email):
    expected = 'Email address already registered'
    mock_find_by_email.return_value = 'foobar'
    with pytest.raises(ValidationError) as e:
        accounts.validate({'email': 'foobar'})
    actual = e.value.errors
    assert expected in actual


def test_find_account_by_id():
    expected = 'foobar'
    accounts.REPO['by_id'][TEST_DATA['id']] = expected
    actual = accounts.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_account_by_id_not_found():
    expected = 'Account not found'
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_id(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual


def test_find_account_by_email():
    expected = 'foobar'
    accounts.REPO['by_email'][TEST_DATA['email']] = expected
    actual = accounts.find_by_email(TEST_DATA['email'])
    assert expected == actual


def test_find_account_by_email_not_found():
    expected = 'Account not found'
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_email(TEST_DATA['email'])
    actual = str(e.value)
    assert expected == actual


@patch('wtf.api.accounts.find_by_email')
def test_find_account_by_email_password(
        mock_find_by_email
    ):
    expected = {'password': TEST_DATA['password']['hash']}
    mock_find_by_email.return_value = expected
    actual = accounts.find_by_email_password(
        TEST_DATA['email'],
        TEST_DATA['password']['plain']
    )
    assert expected == actual


@patch('wtf.api.accounts.find_by_email')
def test_find_account_by_email_password_incorrect_password(
        mock_find_by_email
    ):
    expected = 'Account not found'
    mock_find_by_email.return_value = {'password': ''}
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_email_password(
            TEST_DATA['email'],
            TEST_DATA['password']['plain']
        )
    actual = str(e.value)
    assert expected == actual


def test_find_account_by_email_password_not_found():
    expected = 'Account not found'
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_email_password(
            TEST_DATA['email'],
            TEST_DATA['password']['plain']
        )
    actual = str(e.value)
    assert expected == actual
