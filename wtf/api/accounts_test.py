# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import accounts
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_EMAIL = 'foobar@gmail.com'
TEST_PASSWORD_PLAIN = 'foobar123'
TEST_PASSWORD_HASH = (
    'eb25d108f85572f28f1bc03f0fe08c557bddb5063d886bdab5acc9b2f6d07603'
    + '943ce08a96ebef2c71b71056e1992749304d5aeffd43bef476a77944f91624d3'
)
TEST_ACCOUNT = 'foobar'


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
    expected = 'foobar'
    mock_save.return_value = expected
    response = test_client.post(
        body={'email': TEST_EMAIL, 'password': TEST_PASSWORD_PLAIN}
    )
    response.assert_status_code(200)
    response.assert_body(expected)


def test_handle_post_account_request_content_type_not_json(test_client):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body({
        'errors': ['Content-Type header must be: application/json']
    })


@patch('wtf.api.accounts.validate')
def test_handle_post_account_request_invalid(mock_validate, test_client):
    mock_validate.side_effect = ValidationError(
        errors=['foo', 'bar', 'baz']
    )
    response = test_client.post()
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


def test_handle_get_account_by_id_request(test_client):
    expected = {'account': {'foo': 'bar'}}
    by_id = accounts.REPO['by_id']
    by_id[TEST_ID] = {'foo': 'bar', 'password': 'foobar'}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(200)
    response.assert_body(expected)
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(200)
    response.assert_body(expected)


def test_handle_get_account_by_id_request_not_found(test_client):
    expected = {'errors': ['Account not found']}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(404)
    response.assert_body(expected)


@patch('wtf.api.accounts.uuid4')
@patch('wtf.api.accounts.validate')
def test_save_account_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_ID, 'email': TEST_EMAIL}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_ID
    by_id = accounts.REPO['by_id']
    by_email = accounts.REPO['by_email']
    actual = accounts.save({'id': None, 'email': TEST_EMAIL})
    assert expected == actual
    assert expected == by_id[TEST_ID]
    assert expected == by_email[TEST_EMAIL]


@patch('wtf.api.accounts.validate')
def test_save_account_update(mock_validate):
    expected = {'id': TEST_ID, 'email': TEST_EMAIL}
    mock_validate.return_value = None
    by_id = accounts.REPO['by_id']
    by_email = accounts.REPO['by_email']
    by_id[TEST_ID] = 'foobar1'
    by_email[TEST_EMAIL] = 'foobar2'
    actual = accounts.save({'id': TEST_ID, 'email': TEST_EMAIL})
    assert expected == actual
    assert expected == by_id[TEST_ID]
    assert expected == by_email[TEST_EMAIL]


@patch('wtf.api.accounts.find_by_email')
def test_validate_account(mock_find_by_email):
    mock_find_by_email.side_effect = NotFoundError('foo bar baz')
    accounts.validate({
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD_PLAIN
    })


def test_validate_account_missing_fields():
    expected = [
        'Missing required field: email',
        'Missing required field: password'
    ]
    with pytest.raises(ValidationError) as e:
        accounts.validate({})
    assert set(expected).issubset(e.value.errors)


@patch('wtf.api.accounts.find_by_email')
def test_validate_account_email_already_registered(mock_find_by_email):
    expected = 'Email address already registered'
    mock_find_by_email.return_value = 'foobar'
    with pytest.raises(ValidationError) as e:
        accounts.validate({'email': 'foobar'})
    assert expected in e.value.errors


@patch('wtf.api.accounts.find_by_email')
def test_find_account_by_email_password(
        mock_find_by_email
    ):
    expected = {'password': TEST_PASSWORD_HASH}
    mock_find_by_email.return_value = expected
    actual = accounts.find_by_email_password(TEST_EMAIL, TEST_PASSWORD_PLAIN)
    assert expected == actual


@patch('wtf.api.accounts.find_by_email')
def test_find_account_by_email_password_incorrect_password(
        mock_find_by_email
    ):
    mock_find_by_email.return_value = {'password': ''}
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_email_password(TEST_EMAIL, TEST_PASSWORD_PLAIN)
    assert str(e.value) == 'Account not found'


def test_find_account_by_email_password_not_found():
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_email_password(TEST_EMAIL, TEST_PASSWORD_PLAIN)
    assert str(e.value) == 'Account not found'


def test_find_account_by_id():
    expected = TEST_ACCOUNT
    by_id = accounts.REPO['by_id']
    by_id[TEST_ID] = expected
    assert accounts.find_by_id(TEST_ID) == expected


def test_find_account_by_id_not_found():
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_id(TEST_ID)
    assert str(e.value) == 'Account not found'


def test_find_account_by_email():
    expected = TEST_ACCOUNT
    by_email = accounts.REPO['by_email']
    by_email[TEST_EMAIL] = expected
    assert accounts.find_by_email(TEST_EMAIL) == expected


def test_find_account_by_email_not_found():
    with pytest.raises(NotFoundError) as e:
        accounts.find_by_email(TEST_EMAIL)
    assert str(e.value) == 'Account not found'


@patch('wtf.api.accounts.util.salt_and_hash')
def test_create_account(mock_salt_and_hash):
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


def test_create_account_defaults():
    expected = {
        'id': None,
        'email': None,
        'password': None
    }
    actual = accounts.create()
    assert expected == actual
