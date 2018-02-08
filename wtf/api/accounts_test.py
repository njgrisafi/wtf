# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import accounts
from wtf.api.app import create_app
from wtf.errors import ValidationError
from wtf.http import create_test_client


TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_EMAIL = 'foobar@gmail.com'
TEST_PASSWORD_PLAIN = 'foobar123'
TEST_PASSWORD_HASH = (
    'a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0'
    + 'c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0e0f0a0b0c0d0'
)


def setup_function():
    accounts.IN_MEMORY_ACCOUNTS['by_id'] = {}
    accounts.IN_MEMORY_ACCOUNTS['by_email'] = {}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/accounts')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.accounts.save')
@patch('wtf.api.accounts.find_by_email')
def test_accounts_route_create(
        mock_find_by_email,
        mock_save,
        test_client
    ):
    expected = 'foobar'
    mock_find_by_email.return_value = None
    mock_save.return_value = expected
    response = test_client.post(
        body={'email': TEST_EMAIL, 'password': TEST_PASSWORD_PLAIN}
    )
    response.assert_status_code(200)
    response.assert_body(expected)


def test_accounts_route_create_content_type_not_json(test_client):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body({
        'errors': ['Content-Type header must be: application/json']
    })


@patch('wtf.api.accounts.validate')
def test_accounts_route_create_invalid(mock_validate, test_client):
    mock_validate.side_effect = ValidationError(
        errors=['foo', 'bar', 'baz']
    )
    response = test_client.post()
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


def test_accounts_route_get_by_id(test_client):
    expected = {'account': {'foo': 'bar'}}
    by_id = accounts.IN_MEMORY_ACCOUNTS['by_id']
    by_id[TEST_ID] = {'foo': 'bar', 'password': 'asdf'}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(200)
    response.assert_body(expected)
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(200)
    response.assert_body(expected)


def test_accounts_route_get_by_id_not_found(test_client):
    expected = {'errors': ['Account not found']}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(404)
    response.assert_body(expected)


@patch('wtf.api.accounts.uuid4')
@patch('wtf.api.accounts.validate')
def test_accounts_save_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_ID, 'email': TEST_EMAIL}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_ID
    by_id = accounts.IN_MEMORY_ACCOUNTS['by_id']
    by_email = accounts.IN_MEMORY_ACCOUNTS['by_email']
    actual = accounts.save({'id': None, 'email': TEST_EMAIL})
    assert expected == actual
    assert expected == by_id[TEST_ID]
    assert expected == by_email[TEST_EMAIL]


@patch('wtf.api.accounts.validate')
def test_accounts_save_update(mock_validate):
    expected = {'id': TEST_ID, 'email': TEST_EMAIL}
    mock_validate.return_value = None
    by_id = accounts.IN_MEMORY_ACCOUNTS['by_id']
    by_email = accounts.IN_MEMORY_ACCOUNTS['by_email']
    by_id[TEST_ID] = 'foobar1'
    by_email[TEST_EMAIL] = 'foobar2'
    actual = accounts.save({'id': TEST_ID, 'email': TEST_EMAIL})
    assert expected == actual
    assert expected == by_id[TEST_ID]
    assert expected == by_email[TEST_EMAIL]


def test_accounts_validate_missing_email():
    expected = 'Missing required field: email'
    with pytest.raises(ValidationError) as e:
        accounts.validate({'password': 'foobar'})
    assert expected in e.value.errors


@patch('wtf.api.accounts.find_by_email')
def test_accounts_validate_email_registered(mock_find_by_email):
    expected = 'Email address already registered'
    mock_find_by_email.return_value = 'foobar'
    with pytest.raises(ValidationError) as e:
        accounts.validate({'email': 'foobar'})
    assert expected in e.value.errors


def test_accounts_validate_missing_password():
    expected = 'Missing required field: password'
    with pytest.raises(ValidationError) as e:
        accounts.validate({'email': 'foobar'})
    assert expected in e.value.errors


def test_accounts_find_by_id():
    expected = 'foobar'
    by_id = accounts.IN_MEMORY_ACCOUNTS['by_id']
    by_id[TEST_ID] = expected
    assert accounts.find_by_id(TEST_ID) == expected
    assert accounts.find_by_id('asdf') is None


def test_accounts_find_by_email():
    expected = 'foobar'
    by_email = accounts.IN_MEMORY_ACCOUNTS['by_email']
    by_email[TEST_EMAIL] = expected
    assert accounts.find_by_email(TEST_EMAIL) == expected
    assert accounts.find_by_email('asdf') is None


@patch('wtf.api.accounts.util.salt_and_hash_compare')
@patch('wtf.api.accounts.find_by_email')
def test_accounts_find_by_email_password(
        mock_find_by_email,
        mock_salt_and_hash_compare
    ):
    expected = {'password': ''}
    mock_find_by_email.return_value = expected
    mock_salt_and_hash_compare.return_value = True
    actual = accounts.find_by_email_password('', '')
    assert expected == actual


@patch('wtf.api.accounts.util.salt_and_hash_compare')
@patch('wtf.api.accounts.find_by_email')
def test_accounts_find_by_email_password_incorrect_password(
        mock_find_by_email,
        mock_salt_and_hash_compare
    ):
    mock_find_by_email.return_value = {'password': ''}
    mock_salt_and_hash_compare.return_value = False
    account = accounts.find_by_email_password('', '')
    assert account is None


@patch('wtf.api.accounts.find_by_email')
def test_accounts_find_by_email_password_not_found(mock_find_by_email):
    mock_find_by_email.return_value = None
    account = accounts.find_by_email_password('', '')
    assert account is None


@patch('wtf.api.accounts.util.salt_and_hash')
def test_accounts_create(mock_salt_and_hash):
    expected = {
        'id': TEST_ID,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD_HASH
    }
    mock_salt_and_hash.return_value = TEST_PASSWORD_HASH
    actual = accounts.create(
        id=TEST_ID,
        email=TEST_EMAIL,
        password=TEST_PASSWORD_HASH
    )
    assert expected == actual


def test_accounts_create_defaults():
    expected = {
        'id': None,
        'email': None,
        'password': None
    }
    actual = accounts.create()
    assert expected == actual
