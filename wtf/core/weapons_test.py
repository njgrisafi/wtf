# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest
from mock import patch
from wtf.core import weapons
from wtf.core.errors import NotFoundError, ValidationError


TEST_DATA = {
    'id': 'ebe3f790-a7da-447b-86b3-82efd7e52ff4',
    'recipe': {
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
    },
    'name': 'Universal Foo Sword',
    'description': 'The mightiest sword in all the universe.',
    'grade': 0.345,
    'weight': 12.93,
    'damage': {
        'min': 46.9,
        'max': 96.9
    }
}


def setup_function():
    weapons.REPO_RECIPES = {'by_id': {}}
    weapons.REPO = {'by_id': {}}


def test_create_weapon_recipe():
    expected = {
        'type': TEST_DATA['recipe']['type'],
        'name': TEST_DATA['recipe']['name'],
        'description': TEST_DATA['recipe']['description'],
        'handedness': TEST_DATA['recipe']['handedness'],
        'weight': {
            'center': TEST_DATA['recipe']['weight']['center'],
            'radius': TEST_DATA['recipe']['weight']['radius']
        },
        'damage': {
            'min': {
                'center': TEST_DATA['recipe']['damage']['min']['center'],
                'radius': TEST_DATA['recipe']['damage']['min']['radius']
            },
            'max': {
                'center': TEST_DATA['recipe']['damage']['max']['center'],
                'radius': TEST_DATA['recipe']['damage']['max']['radius']
            }
        }
    }
    actual = weapons.create_recipe(
        type=TEST_DATA['recipe']['type'],
        name=TEST_DATA['recipe']['name'],
        description=TEST_DATA['recipe']['description'],
        handedness=TEST_DATA['recipe']['handedness'],
        weight=dict(
            center=TEST_DATA['recipe']['weight']['center'],
            radius=TEST_DATA['recipe']['weight']['radius']
        ),
        damage=dict(
            min=dict(
                center=TEST_DATA['recipe']['damage']['min']['center'],
                radius=TEST_DATA['recipe']['damage']['min']['radius']
            ),
            max=dict(
                center=TEST_DATA['recipe']['damage']['max']['center'],
                radius=TEST_DATA['recipe']['damage']['max']['radius']
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
        'weight': {'center': None, 'radius': None},
        'damage': {
            'min': {'center': None, 'radius': None},
            'max': {'center': None, 'radius': None}
        }
    }
    actual = weapons.create_recipe()
    assert expected == actual


def test_create_weapon():
    expected = {
        'recipe': TEST_DATA['recipe']['id'],
        'name': TEST_DATA['name'],
        'description': TEST_DATA['description'],
        'grade': TEST_DATA['grade']
    }
    actual = weapons.create(
        recipe=TEST_DATA['recipe']['id'],
        name=TEST_DATA['name'],
        description=TEST_DATA['description'],
        grade=TEST_DATA['grade']
    )
    assert expected == actual


@patch('wtf.core.equipment.generate_grade')
def test_create_weapon_defaults(mock_generate_grade):
    mock_generate_grade.return_value = TEST_DATA['grade']
    expected = {
        'recipe': None,
        'name': None,
        'description': None,
        'grade': TEST_DATA['grade']
    }
    actual = weapons.create()
    assert expected == actual


@patch('wtf.core.weapons.validate_recipe')
@patch('wtf.core.weapons.uuid4')
def test_save_weapon_recipe_insert(mock_uuid4, mock_validate_recipe):
    expected = {'id': TEST_DATA['recipe']['id']}
    mock_uuid4.return_value = TEST_DATA['recipe']['id']
    mock_validate_recipe.return_value = None
    actual = weapons.save_recipe({'id': None})
    assert expected == actual
    assert expected == weapons.REPO_RECIPES['by_id'][TEST_DATA['recipe']['id']]


@patch('wtf.core.weapons.validate_recipe')
def test_save_weapon_recipe_update(mock_validate_recipe):
    expected = {'id': TEST_DATA['recipe']['id']}
    mock_validate_recipe.return_value = None
    actual = weapons.save_recipe({'id': TEST_DATA['recipe']['id']})
    assert expected == actual
    assert expected == weapons.REPO_RECIPES['by_id'][TEST_DATA['recipe']['id']]


@patch('wtf.core.weapons.validate_recipe')
def test_save_weapon_recipe_invalid(mock_validate_recipe):
    mock_validate_recipe.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        weapons.save_recipe({})
    assert not weapons.REPO_RECIPES['by_id'].values()


@patch('wtf.core.weapons.validate')
@patch('wtf.core.weapons.uuid4')
def test_save_weapon_insert(mock_uuid4, mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_uuid4.return_value = TEST_DATA['id']
    mock_validate.return_value = None
    actual = weapons.save({})
    assert expected == actual
    assert expected == weapons.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.core.weapons.validate')
def test_save_weapon_update(mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_validate.return_value = None
    actual = weapons.save({'id': TEST_DATA['id']})
    assert expected == actual
    assert expected == weapons.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.core.weapons.validate')
def test_save_weapon_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        weapons.save({})
    assert not weapons.REPO['by_id'].values()


def test_validate_weapon_recipe():
    weapons.validate_recipe({
        'id': TEST_DATA['recipe']['id'],
        'type': TEST_DATA['recipe']['type'],
        'name': TEST_DATA['recipe']['name'],
        'description': TEST_DATA['recipe']['description'],
        'handedness': TEST_DATA['recipe']['handedness'],
        'weight': {
            'center': TEST_DATA['recipe']['weight']['center'],
            'radius': TEST_DATA['recipe']['weight']['radius']
        },
        'damage': {
            'min': {
                'center': TEST_DATA['recipe']['damage']['min']['center'],
                'radius': TEST_DATA['recipe']['damage']['min']['radius']
            },
            'max': {
                'center': TEST_DATA['recipe']['damage']['max']['center'],
                'radius': TEST_DATA['recipe']['damage']['max']['radius']
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
        weapons.validate_recipe({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_weapon_recipe_invalid_type():
    expected = 'Invalid weapon type'
    with pytest.raises(ValidationError) as e:
        weapons.validate_recipe({'type': 'foobar'})
    actual = e.value.errors
    assert expected in actual


def test_validate_weapon_recipe_invalid_handedness():
    expected = 'Handedness must be either 1 or 2'
    with pytest.raises(ValidationError) as e:
        weapons.validate_recipe({'handedness': 42})
    actual = e.value.errors
    assert expected in actual


def test_validate_weapon_recipe_interval_values_negative():
    expected = [
        'Weight must be >= 0',
        'Min damage must be > 0',
        'Max damage must be > 0'
    ]
    with pytest.raises(ValidationError) as e:
        weapons.validate_recipe({
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
        weapons.validate_recipe({
            'weight': {'center': 5, 'radius': 5},
            'damage': {
                'min': {'center': 10, 'radius': 10},
                'max': {'center': 15, 'radius': 15}
            }
        })
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_weapon_recipe_max_damage_less_than_min_damage():
    expected = 'Min damage must be <= max damage for all values'
    with pytest.raises(ValidationError) as e:
        weapons.validate_recipe({
            'damage': {
                'min': {'center': 20, 'radius': 5},
                'max': {'center': 10, 'radius': 5}
            }
        })
    actual = e.value.errors
    assert expected in actual


def test_validate_weapon_recipe_min_damage_intersects_max_damage():
    expected = 'Min damage must be <= max damage for all values'
    with pytest.raises(ValidationError) as e:
        weapons.validate_recipe({
            'damage': {
                'min': {'center': 90, 'radius': 10},
                'max': {'center': 100, 'radius': 25}
            }
        })
    actual = e.value.errors
    assert expected in actual


@patch('wtf.core.weapons.find_recipe_by_id')
def test_validate_weapon(mock_find_recipe_by_id):
    mock_find_recipe_by_id.return_value = 'foobar'
    weapons.validate({
        'id': TEST_DATA['id'],
        'recipe': TEST_DATA['recipe']['id'],
        'grade': TEST_DATA['grade']
    })


def test_validate_weapon_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: recipe',
        'Missing required field: grade'
    ]
    with pytest.raises(ValidationError) as e:
        weapons.validate({})
    assert set(expected).issubset(e.value.errors)


@patch('wtf.core.weapons.find_recipe_by_id')
def test_validate_weapon_recipe_not_found(mock_find_recipe_by_id):
    expected = 'Weapon recipe not found'
    error = NotFoundError('Weapon recipe not found')
    mock_find_recipe_by_id.side_effect = error
    with pytest.raises(ValidationError) as e:
        weapons.validate({'recipe': 'foobar'})
    assert expected in e.value.errors


def test_validate_weapon_grade_0_to_1():
    expected = 'Equipment grade must be >= 0.0 and <= 1.0'
    for grade in [-0.42, 1.42]:
        with pytest.raises(ValidationError) as e:
            weapons.validate({'grade': grade})
        assert expected in e.value.errors


def test_find_weapon_recipe_by_id():
    expected = 'foobar'
    weapons.REPO_RECIPES['by_id'][TEST_DATA['recipe']['id']] = expected
    actual = weapons.find_recipe_by_id(TEST_DATA['recipe']['id'])
    assert expected == actual


def test_find_weapon_recipe_by_id_not_found():
    expected = 'Weapon recipe not found'
    with pytest.raises(NotFoundError) as e:
        weapons.find_recipe_by_id('foobar')
    actual = str(e.value)
    assert expected == actual


def test_find_weapon_by_id():
    expected = 'foobar'
    weapons.REPO['by_id'][TEST_DATA['id']] = expected
    actual = weapons.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_weapon_by_id_not_found():
    expected = 'Weapon not found'
    with pytest.raises(NotFoundError) as e:
        weapons.find_by_id('foobar')
    actual = str(e.value)
    assert expected == actual


@pytest.mark.parametrize("name,description", [
    pytest.param(TEST_DATA['name'], TEST_DATA['description']),
    pytest.param(None, None)
])
@patch('wtf.core.weapons.find_recipe_by_id')
def test_transform_weapon(mock_find_recipe_by_id, name, description):
    recipe = TEST_DATA.get('recipe')
    mock_find_recipe_by_id.return_value = recipe
    expected = {
        'recipe': recipe['id'],
        'type': recipe['type'],
        'name': recipe['name'] if not name else name,
        'description': (
            recipe['description'] if not description else description
        ),
        'handedness': recipe['handedness'],
        'grade': '+%s' % int(TEST_DATA['grade'] * 10),
        'weight': TEST_DATA['weight'],
        'damage': {
            'min': TEST_DATA['damage']['min'],
            'max': TEST_DATA['damage']['max']
        },
        'other': 'fields'
    }
    actual = weapons.transform({
        'recipe': recipe['id'],
        'grade': TEST_DATA['grade'],
        'name': name,
        'description': description,
        'other': 'fields'
    })
    assert expected == actual
