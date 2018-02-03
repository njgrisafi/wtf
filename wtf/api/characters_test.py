# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import characters
from wtf.api.app import create_app
from wtf.http import create_test_client


TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_ACCOUNT_ID = '1a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_NAME = 'foobar'


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/characters')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.characters.save')
@patch('wtf.api.characters.create')
@patch('wtf.api.characters.find_by_account_id')
def test_route_create_character(
        mock_find_by_account_id,
        mock_create,
        mock_save,
        test_client
    ):
    expected = {'foo': 'bar'}
    mock_find_by_account_id.return_value = []
    mock_create.return_value = None
    mock_save.return_value = expected
    response = test_client.post(
        body={'accountId': TEST_ACCOUNT_ID, 'name': TEST_NAME}
    )
    response.assert_status_code(200)
    response.assert_body(expected)


def test_route_create_character_content_type_not_json(test_client):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body({
        'errors': ['Content-Type header must be: application/json']
    })


def test_route_create_character_missing_fields(test_client):
    response = test_client.post(body={})
    response.assert_status_code(400)
    response.assert_body({
        'errors': [
            'Missing required field: accountId',
            'Missing required field: name'
        ]
    })


def test_route_create_character_missing_account_id(test_client):
    response = test_client.post(body={'name': 'foobar'})
    response.assert_status_code(400)
    response.assert_body({'errors': ['Missing required field: accountId']})


def test_route_create_character_missing_name(test_client):
    response = test_client.post(body={'accountId': 'foobar'})
    response.assert_status_code(400)
    response.assert_body({'errors': ['Missing required field: name']})


@patch('wtf.api.characters.find_by_account_id')
def test_route_create_character_duplicate_character_name(
        mock_find_by_account_id,
        test_client
    ):
    mock_find_by_account_id.return_value = [{'name': 'foo'}]
    response = test_client.post(
        body={'accountId': TEST_ACCOUNT_ID, 'name': 'foo'}
    )
    response.assert_status_code(400)
    response.assert_body({'errors': ['Duplicate character name: foo']})


def test_find_by_account_id():
    expected = ['one', 'two', 'three']
    by_account_id = characters.IN_MEMORY_CHARACTERS['by_account_id']
    by_account_id[TEST_ACCOUNT_ID] = expected
    actual = characters.find_by_account_id(TEST_ACCOUNT_ID)
    assert expected == actual


@patch('wtf.api.characters.uuid4')
def test_save_character_insert(mock_uuid4):
    expected = {'id': TEST_ID}
    mock_uuid4.return_value = TEST_ID
    by_id = characters.IN_MEMORY_CHARACTERS['by_id']
    actual = characters.save({'id': None})
    assert expected == actual
    assert expected == by_id[TEST_ID]


def test_save_character_update():
    expected = {'id': TEST_ID}
    by_id = characters.IN_MEMORY_CHARACTERS['by_id']
    by_id[TEST_ID] = expected
    actual = characters.save({'id': TEST_ID})
    assert expected == actual
    assert expected == by_id[TEST_ID]


def test_create_character():
    expected = {'id': None, 'accountId': TEST_ACCOUNT_ID, 'name': TEST_NAME}
    actual = characters.create(account_id=TEST_ACCOUNT_ID, name=TEST_NAME)
    assert expected == actual


def test_create_character_defaults():
    expected = {'id': None, 'accountId': None, 'name': None}
    actual = characters.create()
    assert expected == actual
