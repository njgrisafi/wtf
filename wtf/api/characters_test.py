# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import characters
from wtf.api.app import create_app
from wtf.errors import ValidationError
from wtf.http import create_test_client


TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_ACCOUNT = '1a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_NAME = 'foobar'


def setup_function():
    characters.REPO_CHARACTERS['by_id'] = {}
    characters.REPO_CHARACTERS['by_account'] = {}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/characters')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.characters.save')
@patch('wtf.api.characters.find_by_account')
def test_characters_route_create(
        mock_find_by_account,
        mock_save,
        test_client
    ):
    expected = 'foobar'
    mock_find_by_account.return_value = []
    mock_save.return_value = expected
    response = test_client.post(
        body={'account': TEST_ACCOUNT, 'name': TEST_NAME}
    )
    response.assert_status_code(200)
    response.assert_body(expected)


def test_characters_route_create_content_type_not_json(test_client):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body({
        'errors': ['Content-Type header must be: application/json']
    })


@patch('wtf.api.characters.validate')
def test_characters_route_create_invalid(mock_validate, test_client):
    mock_validate.side_effect = ValidationError(
        errors=['foo', 'bar', 'baz']
    )
    response = test_client.post()
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


def test_characters_route_get_by_id(test_client):
    expected = {'character': {'foo': 'bar'}}
    by_id = characters.REPO_CHARACTERS['by_id']
    by_id[TEST_ID] = {'foo': 'bar'}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(200)
    response.assert_body(expected)


def test_characters_route_get_by_id_not_found(test_client):
    expected = {'errors': ['Character not found']}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(404)
    response.assert_body(expected)


@patch('wtf.api.characters.uuid4')
@patch('wtf.api.characters.validate')
def test_characters_save_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_ID}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_ID
    by_id = characters.REPO_CHARACTERS['by_id']
    actual = characters.save({'id': None})
    assert expected == actual
    assert expected == by_id[TEST_ID]


@patch('wtf.api.characters.validate')
def test_characters_save_update(mock_validate):
    expected = {'id': TEST_ID}
    mock_validate.return_value = None
    by_id = characters.REPO_CHARACTERS['by_id']
    by_id[TEST_ID] = expected
    actual = characters.save({'id': TEST_ID})
    assert expected == actual
    assert expected == by_id[TEST_ID]


def test_characters_validate_missing_account():
    expected = 'Missing required field: account'
    with pytest.raises(ValidationError) as e:
        characters.validate({'name': 'foobar'})
    assert expected in e.value.errors


def test_characters_validate_missing_name():
    expected = 'Missing required field: name'
    with pytest.raises(ValidationError) as e:
        characters.validate({'account': 'foobar'})
    assert expected in e.value.errors


@patch('wtf.api.characters.find_by_account')
def test_characters_validate_duplicate_name(mock_find_by_account):
    expected = 'Duplicate character name: foo'
    mock_find_by_account.return_value = [{'name': 'foo'}]
    with pytest.raises(ValidationError) as e:
        characters.validate({'account': TEST_ACCOUNT, 'name': 'foo'})
    assert expected in e.value.errors


def test_characters_find_by_account():
    expected = ['one', 'two', 'three']
    by_account = characters.REPO_CHARACTERS['by_account']
    by_account[TEST_ACCOUNT] = expected
    actual = characters.find_by_account(TEST_ACCOUNT)
    assert expected == actual


def test_characters_allocate_ability_points():
    expected = {
        'abilities': dict(
            unallocated=5,
            strength=6,
            endurance=7,
            agility=8,
            accuracy=9
        )
    }
    character = {
        'abilities': dict(
            unallocated=15,
            strength=5,
            endurance=5,
            agility=5,
            accuracy=5
        )
    }
    actual = characters.allocate_ability_points(
        character,
        strength=1,
        endurance=2,
        agility=3,
        accuracy=4
    )
    assert expected == actual


def test_characters_allocate_ability_points_insufficient():
    expected = 'Insufficient ability points'
    character = {
        'abilities': dict(
            unallocated=3,
            strength=5,
            endurance=5,
            agility=5,
            accuracy=5
        )
    }
    with pytest.raises(ValidationError) as e:
        characters.allocate_ability_points(
            character,
            strength=1,
            endurance=1,
            agility=1,
            accuracy=1
        )
    assert expected in e.value.errors


def test_characters_create():
    expected = {
        'id': None,
        'account': TEST_ACCOUNT,
        'name': TEST_NAME,
        'abilities': {
            'unallocated': 5,
            'strength': 5,
            'endurance': 5,
            'agility': 5,
            'accuracy': 5
        }
    }
    actual = characters.create(
        account=TEST_ACCOUNT,
        name=TEST_NAME,
        abilities=dict(
            unallocated=5,
            strength=5,
            endurance=5,
            agility=5,
            accuracy=5
        )
    )
    assert expected == actual


def test_characters_create_defaults():
    expected = {
        'id': None,
        'account': None,
        'name': None,
        'abilities': {
            'unallocated': 0,
            'strength': 0,
            'endurance': 0,
            'agility': 0,
            'accuracy': 0
        }
    }
    actual = characters.create()
    assert expected == actual
