# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from flask import Flask
from mock import patch
from wtf.api import accounts
from wtf.api.testing import assert_post


TEST_UUID = '048e8cf5-bf6f-4b39-ac97-6f9851f61b16'
TEST_EMAIL = 'foobar@gmail.com'
TEST_PASSWORD_PLAIN = 'foobar123'
TEST_PASSWORD_HASH = (
    '67d765888ea8f71875dfe27334786bffdca070705ee97bd17bec85f8580f7f01'
    + '012eab80b72cbfe663429219e920aee8cd17ba8893e302844682104ee88d3145'
)


def setup_function():
    accounts.IN_MEMORY_ACCOUNTS['by_uuid'] = {}
    accounts.IN_MEMORY_ACCOUNTS['by_email'] = {}


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(accounts.BLUEPRINT, url_prefix='/')
    app.testing = True
    test_client = app.test_client()
    app.app_context()
    return test_client


def test_route_create_account_content_type_json(test_client):
    assert_post(
        test_client,
        headers={'Content-Type': 'text/html'},
        response_body={
            'errors': ['Content-Type header must be: application/json']
        },
        response_code=400
    )


def test_route_create_account_missing_fields(test_client):
    assert_post(
        test_client,
        body={},
        response_body={
            'errors': [
                'Missing required field: email',
                'Missing required field: password'
            ]
        },
        response_code=400
    )


def test_route_create_account_missing_email(test_client):
    assert_post(
        test_client,
        body={'password': TEST_PASSWORD_PLAIN},
        response_body={'errors': ['Missing required field: email']},
        response_code=400
    )


def test_route_create_account_missing_password(test_client):
    assert_post(
        test_client,
        body={'email': TEST_EMAIL},
        response_body={'errors': ['Missing required field: password']},
        response_code=400
    )


def test_route_create_account_email_exists(test_client):
    accounts.save({'email': TEST_EMAIL})
    assert_post(
        test_client,
        body={'email': TEST_EMAIL, 'password': TEST_PASSWORD_PLAIN},
        response_body={
            'errors': [
                'An account is already registered with the provided email '
                + 'address.'
            ]
        },
        response_code=400
    )

@patch('wtf.api.accounts.uuid4')
@patch('wtf.api.accounts.util.salt_and_hash')
def test_route_create_account(mock_salt_and_hash, mock_uuid4, test_client):
    # stub out salt_and_hash to return the same value for testing purposes
    mock_salt_and_hash.return_value = TEST_PASSWORD_HASH
    # stub out uuid4 to return the same uuid for testing purposes
    mock_uuid4.return_value = TEST_UUID
    assert_post(
        test_client,
        body={'email': TEST_EMAIL, 'password': TEST_PASSWORD_PLAIN},
        response_body={
            'uuid': TEST_UUID,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD_HASH
        },
        response_code=200
    )


@patch('wtf.api.accounts.util.salt_and_hash')
def test_account_creation(mock_salt_and_hash):
    # stub out salt_and_hash to return the same value for testing purposes
    mock_salt_and_hash.return_value = TEST_PASSWORD_HASH
    expected = {
        'uuid': TEST_UUID,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD_HASH
    }
    actual = accounts.create(
        uuid=TEST_UUID,
        email=TEST_EMAIL,
        password=TEST_PASSWORD_HASH
    )
    assert expected == actual


def test_account_creation_defaults():
    expected = {
        'uuid': None,
        'email': None,
        'password': None
    }
    actual = accounts.create()
    assert expected == actual


@patch('wtf.api.accounts.util.salt_and_hash')
def test_account_save_update(mock_salt_and_hash):
    # stub out salt_and_hash to return the same value for testing purposes
    mock_salt_and_hash.return_value = TEST_PASSWORD_HASH
    expected = {
        'uuid': TEST_UUID,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD_HASH
    }
    actual = accounts.save(accounts.create(
        uuid=TEST_UUID,
        email=TEST_EMAIL,
        password=TEST_PASSWORD_HASH
    ))
    assert expected == actual


@patch('wtf.api.accounts.uuid4')
@patch('wtf.api.accounts.util.salt_and_hash')
def test_account_save_insert(mock_salt_and_hash, mock_uuid4):
    # stub out salt_and_hash to return the same value for testing purposes
    mock_salt_and_hash.return_value = TEST_PASSWORD_HASH
    # stub out uuid4 to return the same uuid for testing purposes
    mock_uuid4.return_value = TEST_UUID
    expected = {
        'uuid': TEST_UUID,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD_HASH
    }
    actual = accounts.save(accounts.create(
        email=TEST_EMAIL,
        password=TEST_PASSWORD_HASH
    ))
    assert expected == actual


def test_find_account_by_uuid():
    account = accounts.save(accounts.create())
    assert accounts.find_by_uuid(account.get('uuid')) == account
    assert accounts.find_by_uuid('asdf') is None


def test_find_account_by_email():
    account = accounts.create(email=TEST_EMAIL)
    accounts.save(account)
    assert accounts.find_by_email(TEST_EMAIL) == account
    assert accounts.find_by_email('asdf') is None


def test_find_account_by_email_password():
    expected = accounts.create(email=TEST_EMAIL, password=TEST_PASSWORD_PLAIN)
    accounts.save(expected)
    actual = accounts.find_by_email_password(TEST_EMAIL, TEST_PASSWORD_PLAIN)
    assert expected == actual


def test_find_account_by_email_password_incorrect_password():
    accounts.save({'email': TEST_EMAIL, 'password': TEST_PASSWORD_HASH})
    assert accounts.find_by_email_password(TEST_EMAIL, 'asdf42') is None


def test_find_account_by_email_password_not_found():
    account = accounts.find_by_email_password(TEST_EMAIL, TEST_PASSWORD_PLAIN)
    assert account is None