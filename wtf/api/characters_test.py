# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import characters
from wtf.api.app import create_app
from wtf.errors import ValidationError
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
@patch('wtf.api.characters.find_by_account_id')
def test_route_create_character(
        mock_find_by_account_id,
        mock_save,
        test_client
    ):
    expected = 'foobar'
    mock_find_by_account_id.return_value = []
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


@patch('wtf.api.characters.validate')
def test_route_create_character_invalid(mock_validate, test_client):
    mock_validate.side_effect = ValidationError(
        errors=['foo', 'bar', 'baz']
    )
    response = test_client.post()
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.api.characters.uuid4')
@patch('wtf.api.characters.validate')
def test_save_character_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_ID}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_ID
    by_id = characters.IN_MEMORY_CHARACTERS['by_id']
    actual = characters.save({'id': None})
    assert expected == actual
    assert expected == by_id[TEST_ID]


@patch('wtf.api.characters.validate')
def test_save_character_update(mock_validate):
    expected = {'id': TEST_ID}
    mock_validate.return_value = None
    by_id = characters.IN_MEMORY_CHARACTERS['by_id']
    by_id[TEST_ID] = expected
    actual = characters.save({'id': TEST_ID})
    assert expected == actual
    assert expected == by_id[TEST_ID]


def test_validate_missing_fields():
    expected = [
        'Missing required field: accountId',
        'Missing required field: name'
    ]
    with pytest.raises(ValidationError) as e:
        characters.validate({})
    actual = e.value.errors
    assert expected == actual


def test_validate_missing_account_id():
    expected = ['Missing required field: accountId']
    with pytest.raises(ValidationError) as e:
        characters.validate({'name': 'foobar'})
    actual = e.value.errors
    assert expected == actual


def test_validate_missing_name():
    expected = ['Missing required field: name']
    with pytest.raises(ValidationError) as e:
        characters.validate({'accountId': 'foobar'})
    actual = e.value.errors
    assert expected == actual


@patch('wtf.api.characters.find_by_account_id')
def test_validate_duplicate_name(mock_find_by_account_id):
    expected = ['Duplicate character name: foo']
    mock_find_by_account_id.return_value = [{'name': 'foo'}]
    with pytest.raises(ValidationError) as e:
        characters.validate({'accountId': TEST_ACCOUNT_ID, 'name': 'foo'})
    actual = e.value.errors
    assert expected == actual


def test_find_by_account_id():
    expected = ['one', 'two', 'three']
    by_account_id = characters.IN_MEMORY_CHARACTERS['by_account_id']
    by_account_id[TEST_ACCOUNT_ID] = expected
    actual = characters.find_by_account_id(TEST_ACCOUNT_ID)
    assert expected == actual


def test_allocate_ability_points():
    expected = {
        'abilities': dict(strength=6, endurance=7, agility=8, accuracy=9),
        'ability_points': 5
    }
    character = {
        'abilities': dict(strength=5, endurance=5, agility=5, accuracy=5),
        'ability_points': 15
    }
    actual = characters.allocate_ability_points(
        character,
        strength=1,
        endurance=2,
        agility=3,
        accuracy=4
    )
    assert expected == actual


def test_allocate_ability_points_insufficient():
    expected = ['Insufficient ability points']
    character = {
        'abilities': dict(strength=5, endurance=5, agility=5, accuracy=5),
        'ability_points': 3
    }
    with pytest.raises(ValidationError) as error:
        characters.allocate_ability_points(
            character,
            strength=1,
            endurance=1,
            agility=1,
            accuracy=1
        )
    actual = error.value.errors
    assert expected == actual


def test_create_character():
    expected = {
        'id': None,
        'accountId': TEST_ACCOUNT_ID,
        'name': TEST_NAME,
        'abilities': {
            'strength': 5,
            'endurance': 5,
            'agility': 5,
            'accuracy': 5
        },
        'ability_points': 5
    }
    actual = characters.create(
        account_id=TEST_ACCOUNT_ID,
        name=TEST_NAME,
        abilities=dict(strength=5, endurance=5, agility=5, accuracy=5),
        ability_points=5
    )
    assert expected == actual


def test_create_character_defaults():
    expected = {
        'id': None,
        'accountId': None,
        'name': None,
        'abilities': {
            'strength': 0,
            'endurance': 0,
            'agility': 0,
            'accuracy': 0
        },
        'ability_points': 0
    }
    actual = characters.create()
    assert expected == actual
