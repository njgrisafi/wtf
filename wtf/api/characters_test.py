# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import characters
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


TEST_ID = '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_ACCOUNT = '1a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'
TEST_NAME = 'foobar'


def setup_function():
    characters.REPO = {'by_id': {}, 'by_account': {}}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/characters')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.characters.save')
@patch('wtf.api.characters.find_by_account')
def test_handle_post_character_request(
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


def test_handle_post_character_request_content_type_not_json(test_client):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body({
        'errors': ['Content-Type header must be: application/json']
    })


@patch('wtf.api.characters.validate')
def test_handle_post_character_request_invalid(mock_validate, test_client):
    mock_validate.side_effect = ValidationError(
        errors=['foo', 'bar', 'baz']
    )
    response = test_client.post()
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


def test_handle_get_character_by_id_request(test_client):
    expected = {'character': {'foo': 'bar'}}
    by_id = characters.REPO['by_id']
    by_id[TEST_ID] = {'foo': 'bar'}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(200)
    response.assert_body(expected)


def test_handle_get_character_by_id_request_not_found(test_client):
    expected = {'errors': ['Character not found']}
    response = test_client.get(path='/%s' % TEST_ID)
    response.assert_status_code(404)
    response.assert_body(expected)


@patch('wtf.api.characters.uuid4')
@patch('wtf.api.characters.validate')
def test_save_character_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_ID}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_ID
    by_id = characters.REPO['by_id']
    actual = characters.save({'id': None})
    assert expected == actual
    assert expected == by_id[TEST_ID]


@patch('wtf.api.characters.validate')
def test_save_character_update(mock_validate):
    expected = {'id': TEST_ID}
    mock_validate.return_value = None
    by_id = characters.REPO['by_id']
    by_id[TEST_ID] = expected
    actual = characters.save({'id': TEST_ID})
    assert expected == actual
    assert expected == by_id[TEST_ID]


def test_validate_character_missing_fields():
    expected = [
        'Missing required field: account',
        'Missing required field: name'
    ]
    with pytest.raises(ValidationError) as e:
        characters.validate({})
    assert set(expected).issubset(e.value.errors)


@patch('wtf.api.characters.find_by_account')
def test_validate_character_duplicate_name(mock_find_by_account):
    expected = 'Duplicate character name: foo'
    mock_find_by_account.return_value = [{'name': 'foo'}]
    with pytest.raises(ValidationError) as e:
        characters.validate({'account': TEST_ACCOUNT, 'name': 'foo'})
    assert expected in e.value.errors


def test_find_character_by_id():
    expected = 'foobar'
    by_id = characters.REPO['by_id']
    by_id[TEST_ID] = expected
    assert characters.find_by_id(TEST_ID) == expected


def test_find_character_by_id_not_found():
    with pytest.raises(NotFoundError) as e:
        characters.find_by_id('foobar')
    assert str(e.value) == 'Character not found'


def test_find_characters_by_account():
    expected = ['one', 'two', 'three']
    by_account = characters.REPO['by_account']
    by_account[TEST_ACCOUNT] = expected
    actual = characters.find_by_account(TEST_ACCOUNT)
    assert expected == actual


def test_allocate_character_ability_points():
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


def test_allocate_character_ability_points_insufficient_points():
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


def test_create_character():
    expected = {
        'id': None,
        'account': TEST_ACCOUNT,
        'name': TEST_NAME,
        'level': 12,
        'experience': 123,
        'health': 1234,
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
        level=12,
        experience=123,
        health=1234,
        abilities=dict(
            unallocated=5,
            strength=5,
            endurance=5,
            agility=5,
            accuracy=5
        )
    )
    assert expected == actual


def test_create_character_defaults():
    expected = {
        'id': None,
        'account': None,
        'name': None,
        'level': 1,
        'experience': 0,
        'health': 1,
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
