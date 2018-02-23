# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.core import characters
from wtf.core.errors import NotFoundError, ValidationError


TEST_DATA = {
    'id': '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d',
    'account': '1a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d',
    'name': 'foobar',
    'abilities': {
        'unallocated': 5,
        'strength': 5,
        'endurance': 5,
        'agility': 5,
        'accuracy': 5
    }
}


def setup_function():
    characters.REPO = {'by_id': {}, 'by_account': {}}


def test_create_character():
    expected = {
        'id': None,
        'account': TEST_DATA['account'],
        'name': TEST_DATA['name'],
        'level': 12,
        'experience': 123,
        'health': 1234,
        'abilities': TEST_DATA['abilities']
    }
    actual = characters.create(
        account=TEST_DATA['account'],
        name=TEST_DATA['name'],
        level=12,
        experience=123,
        health=1234,
        abilities=TEST_DATA['abilities']
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
        'abilities': {
            'unallocated': 15,
            'strength': 5,
            'endurance': 5,
            'agility': 5,
            'accuracy': 5
        }
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
        'abilities': {
            'unallocated': 3,
            'strength': 5,
            'endurance': 5,
            'agility': 5,
            'accuracy': 5
        }
    }
    with pytest.raises(ValidationError) as e:
        characters.allocate_ability_points(
            character,
            strength=1,
            endurance=1,
            agility=1,
            accuracy=1
        )
    actual = e.value.errors
    assert expected in actual


@patch('wtf.core.characters.validate')
@patch('wtf.core.characters.uuid4')
def test_save_character_insert(mock_uuid4, mock_validate):
    expected = {'id': TEST_DATA['id'], 'account': TEST_DATA['account']}
    mock_uuid4.return_value = TEST_DATA['id']
    mock_validate.return_value = None
    actual = characters.save({'account': TEST_DATA['account']})
    assert expected == actual
    assert expected == characters.REPO['by_id'][TEST_DATA['id']]
    assert expected in characters.REPO['by_account'][TEST_DATA['account']]


@patch('wtf.core.characters.validate')
def test_save_character_update(mock_validate):
    expected = {'id': TEST_DATA['id'], 'account': TEST_DATA['account']}
    mock_validate.return_value = None
    actual = characters.save(
        {'id': TEST_DATA['id'], 'account': TEST_DATA['account']}
    )
    assert expected == actual
    assert expected == characters.REPO['by_id'][TEST_DATA['id']]
    assert expected in characters.REPO['by_account'][TEST_DATA['account']]


@patch('wtf.core.characters.validate')
def test_save_character_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        characters.save({})
    assert not characters.REPO['by_id'].values()
    assert not characters.REPO['by_account'].values()


def test_validate_character():
    characters.validate({
        'id': TEST_DATA['id'],
        'account': TEST_DATA['account'],
        'name': TEST_DATA['name']
    })


def test_validate_character_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: account',
        'Missing required field: name'
    ]
    with pytest.raises(ValidationError) as e:
        characters.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


@patch('wtf.core.characters.find_by_account')
def test_validate_character_duplicate_name(mock_find_by_account):
    expected = 'Duplicate character name: foo'
    mock_find_by_account.return_value = [{'name': 'foo'}]
    with pytest.raises(ValidationError) as e:
        characters.validate({'account': TEST_DATA['account'], 'name': 'foo'})
    actual = e.value.errors
    assert expected in actual


def test_find_character_by_id():
    expected = 'foobar'
    characters.REPO['by_id'][TEST_DATA['id']] = expected
    actual = characters.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_character_by_id_not_found():
    expected = 'Character not found'
    with pytest.raises(NotFoundError) as e:
        characters.find_by_id('foobar')
    actual = str(e.value)
    assert expected == actual


def test_find_characters_by_account():
    expected = ['one', 'two', 'three']
    characters.REPO['by_account'][TEST_DATA['account']] = expected
    actual = characters.find_by_account(TEST_DATA['account'])
    assert expected == actual
