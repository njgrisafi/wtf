# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.core import weaponrecipes
from wtf.core.errors import NotFoundError, ValidationError


TEST_DATA = {
    'id': '2513cb35-9a34-4612-8541-4916035979f3',
    'type': 'sword',
    'name': 'Foo Sword',
    'description': 'The mightiest sword in all the land.',
    'handedness': 2,
    'weight': {'center': 12, 'radius': 3},
    'damage': {
        'min': {'center': 50, 'radius': 10},
        'max': {'center': 100, 'radius': 10}
    }
}


def setup_function():
    weaponrecipes.REPO = {'by_id': {}}


def test_create_weapon_recipe():
    expected = {
        'type': TEST_DATA['type'],
        'name': TEST_DATA['name'],
        'description': TEST_DATA['description'],
        'handedness': TEST_DATA['handedness'],
        'weight': {
            'center': TEST_DATA['weight']['center'],
            'radius': TEST_DATA['weight']['radius']
        },
        'damage': {
            'min': {
                'center': TEST_DATA['damage']['min']['center'],
                'radius': TEST_DATA['damage']['min']['radius']
            },
            'max': {
                'center': TEST_DATA['damage']['max']['center'],
                'radius': TEST_DATA['damage']['max']['radius']
            }
        }
    }
    actual = weaponrecipes.create(
        type=TEST_DATA['type'],
        name=TEST_DATA['name'],
        description=TEST_DATA['description'],
        handedness=TEST_DATA['handedness'],
        weight=dict(
            center=TEST_DATA['weight']['center'],
            radius=TEST_DATA['weight']['radius']
        ),
        damage=dict(
            min=dict(
                center=TEST_DATA['damage']['min']['center'],
                radius=TEST_DATA['damage']['min']['radius']
            ),
            max=dict(
                center=TEST_DATA['damage']['max']['center'],
                radius=TEST_DATA['damage']['max']['radius']
            )
        )
    )
    assert expected == actual


def test_create_weapon_recipe_defaults():
    expected = {
        'type': None,
        'name': None,
        'description': None,
        'handedness': 1,
        'weight': {'center': 0, 'radius': 0},
        'damage': {
            'min': {'center': 0, 'radius': 0},
            'max': {'center': 0, 'radius': 0}
        }
    }
    actual = weaponrecipes.create()
    assert expected == actual


@patch('wtf.core.weaponrecipes.validate')
@patch('wtf.core.weaponrecipes.uuid4')
def test_save_weapon_recipe_insert(mock_uuid4, mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_uuid4.return_value = TEST_DATA['id']
    mock_validate.return_value = None
    actual = weaponrecipes.save({'id': None})
    assert expected == actual
    assert expected == weaponrecipes.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.core.weaponrecipes.validate')
def test_save_weapon_recipe_update(mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_validate.return_value = None
    actual = weaponrecipes.save({'id': TEST_DATA['id']})
    assert expected == actual
    assert expected == weaponrecipes.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.core.weaponrecipes.validate')
def test_save_weapon_recipe_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        weaponrecipes.save({})
    assert not weaponrecipes.REPO['by_id'].values()


def test_validate_weapon_recipe():
    weaponrecipes.validate({
        'id': TEST_DATA['id'],
        'type': TEST_DATA['type'],
        'name': TEST_DATA['name'],
        'description': TEST_DATA['description'],
        'handedness': TEST_DATA['handedness'],
        'weight': {
            'center': TEST_DATA['weight']['center'],
            'radius': TEST_DATA['weight']['radius']
        },
        'damage': {
            'min': {
                'center': TEST_DATA['damage']['min']['center'],
                'radius': TEST_DATA['damage']['min']['radius']
            },
            'max': {
                'center': TEST_DATA['damage']['max']['center'],
                'radius': TEST_DATA['damage']['max']['radius']
            }
        }
    })


def test_validate_weapon_recipe_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: type',
        'Missing required field: name',
        'Missing required field: description',
        'Missing required field: handedness',
        'Missing required field: weight.center',
        'Missing required field: weight.radius',
        'Missing required field: damage.min.center',
        'Missing required field: damage.min.radius',
        'Missing required field: damage.max.center',
        'Missing required field: damage.max.radius'
    ]
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_weapon_recipe_invalid_type():
    expected = 'Invalid weapon type'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({'type': 'foobar'})
    actual = e.value.errors
    assert expected in actual


def test_validate_weapon_recipe_invalid_handedness():
    expected = 'Handedness must be either 1 or 2'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({'handedness': 42})
    actual = e.value.errors
    assert expected in actual


def test_validate_weapon_recipe_interval_values_negative():
    expected = [
        'Weight must be >= 0',
        'Min damage must be > 0',
        'Max damage must be > 0'
    ]
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({
            'weight': {'center': 5, 'radius': 10},
            'damage': {
                'min': {'center': 10, 'radius': 20},
                'max': {'center': 15, 'radius': 30}
            }
        })
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_weapon_recipe_interval_values_zero():
    expected = [
        'Min damage must be > 0',
        'Max damage must be > 0'
    ]
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({
            'weight': {'center': 5, 'radius': 5},
            'damage': {
                'min': {'center': 10, 'radius': 10},
                'max': {'center': 15, 'radius': 15}
            }
        })
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_weapon_recipe_max_damage_less_than_min_damage():
    expected = 'Min damage must always be less than max damage'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({
            'damage': {
                'min': {'center': 20, 'radius': 5},
                'max': {'center': 10, 'radius': 5}
            }
        })
    actual = e.value.errors
    assert expected in actual


def test_validate_weapon_recipe_min_damage_intersects_max_damage():
    expected = 'Min damage must always be less than max damage'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({
            'damage': {
                'min': {'center': 90, 'radius': 10},
                'max': {'center': 100, 'radius': 25}
            }
        })
    actual = e.value.errors
    assert expected in actual


def test_find_weapon_recipe_by_id():
    expected = 'foobar'
    weaponrecipes.REPO['by_id'][TEST_DATA['id']] = expected
    actual = weaponrecipes.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_weapon_recipe_by_id_not_found():
    expected = 'Weapon recipe not found'
    with pytest.raises(NotFoundError) as e:
        weaponrecipes.find_by_id('foobar')
    actual = str(e.value)
    assert expected == actual
