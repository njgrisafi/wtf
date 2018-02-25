# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest
from mock import patch
from wtf.core import armor
from wtf.core.errors import NotFoundError, ValidationError


TEST_DATA = {
    'id': '26e7ca08-883f-4be4-b684-7acca01cfe0b',
    'recipe': {
        'id': 'a2f4309d-08ae-48e2-a173-55399533a826',
        'name': 'Foo Helm',
        'description': 'The mightiest helmet in the land.',
        'location': 'head',
        'weight': {'center': 12.3, 'radius': 4.5},
        'defense': {
            'min': {'center': 67.8, 'radius': 9.0},
            'max': {'center': 123.4, 'radius': 5.6}
        }
    },
    'name': 'Galactic Foo Helm',
    'description': 'The mightiest helmet in all the galaxy.',
    'location': 'head',
    'grade': 0.123,
    'weight': 15.69,
    'defense': {'min': 61.01, 'max': 119.18}
}


def setup_function():
    armor.REPO_RECIPES = {'by_id': {}}
    armor.REPO = {'by_id': {}}


def test_create_armor_recipe():
    recipe = TEST_DATA['recipe']
    expected = {
        'name': recipe['name'],
        'description': recipe['description'],
        'location': TEST_DATA['location'],
        'weight': {
            'center': recipe['weight']['center'],
            'radius': recipe['weight']['radius']
        },
        'defense': {
            'min': {
                'center': recipe['defense']['min']['center'],
                'radius': recipe['defense']['min']['radius']
            },
            'max': {
                'center': recipe['defense']['max']['center'],
                'radius': recipe['defense']['max']['radius']
            }
        }
    }
    actual = armor.create_recipe(
        name=recipe['name'],
        description=recipe['description'],
        location=TEST_DATA['location'],
        weight=dict(
            center=recipe['weight']['center'],
            radius=recipe['weight']['radius']
        ),
        defense=dict(
            min=dict(
                center=recipe['defense']['min']['center'],
                radius=recipe['defense']['min']['radius']
            ),
            max=dict(
                center=recipe['defense']['max']['center'],
                radius=recipe['defense']['max']['radius']
            )
        )
    )
    assert expected == actual


def test_create_armor_recipe_default():
    expected = {
        'name': None,
        'description': None,
        'location': None,
        'weight': {'center': None, 'radius': None},
        'defense': {
            'min': {'center': None, 'radius': None},
            'max': {'center': None, 'radius': None}
        }
    }
    actual = armor.create_recipe()
    assert expected == actual


def test_create_armor():
    expected = {
        'recipe': TEST_DATA['recipe']['id'],
        'name': TEST_DATA['name'],
        'description': TEST_DATA['description'],
        'grade': TEST_DATA['grade']
    }
    actual = armor.create(
        recipe=TEST_DATA['recipe']['id'],
        name=TEST_DATA['name'],
        description=TEST_DATA['description'],
        grade=TEST_DATA['grade']
    )
    assert expected == actual


@patch('wtf.core.equipment.generate_grade')
def test_create_armor_defaults(mock_generate_grade):
    expected = {
        'recipe': None,
        'name': None,
        'description': None,
        'grade': TEST_DATA['grade']
    }
    mock_generate_grade.return_value = TEST_DATA['grade']
    actual = armor.create()
    assert expected == actual


@patch('wtf.core.armor.validate_recipe')
@patch('wtf.core.armor.uuid4')
def test_save_armor_recipe_insert(mock_uuid4, mock_validate_recipe):
    expected = {'id': TEST_DATA['recipe']['id']}
    mock_uuid4.return_value = TEST_DATA['recipe']['id']
    mock_validate_recipe.return_value = None
    actual = armor.save_recipe({})
    assert expected == actual
    assert expected == armor.REPO_RECIPES['by_id'][TEST_DATA['recipe']['id']]


@patch('wtf.core.armor.validate_recipe')
def test_save_armor_recipe_update(mock_validate_recipe):
    expected = {'id': TEST_DATA['recipe']['id']}
    mock_validate_recipe.return_value = None
    actual = armor.save_recipe({'id': TEST_DATA['recipe']['id']})
    assert expected == actual
    assert expected == armor.REPO_RECIPES['by_id'][TEST_DATA['recipe']['id']]


@patch('wtf.core.armor.validate_recipe')
def test_save_armor_recipe_invalid(mock_validate_recipe):
    mock_validate_recipe.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        armor.save_recipe({})
    assert not armor.REPO_RECIPES['by_id'].values()


@patch('wtf.core.armor.validate')
@patch('wtf.core.armor.uuid4')
def test_save_armor_insert(mock_uuid4, mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_uuid4.return_value = TEST_DATA['id']
    mock_validate.return_value = None
    actual = armor.save({})
    assert expected == actual
    assert expected == armor.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.core.armor.validate')
def test_save_armor_update(mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_validate.return_value = None
    actual = armor.save({'id': TEST_DATA['id']})
    assert expected == actual
    assert expected == armor.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.core.armor.validate')
def test_save_armor_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        armor.save({})
    assert not armor.REPO['by_id'].values()


def test_validate_armor_recipe():
    recipe = TEST_DATA['recipe']
    armor.validate_recipe({
        'id': recipe['id'],
        'name': recipe['name'],
        'description': recipe['description'],
        'location': recipe['location'],
        'weight': {
            'center': recipe['weight']['center'],
            'radius': recipe['weight']['radius']
        },
        'defense': {
            'min': {
                'center': recipe['defense']['min']['center'],
                'radius': recipe['defense']['min']['radius']
            },
            'max': {
                'center': recipe['defense']['max']['center'],
                'radius': recipe['defense']['max']['radius']
            }
        }
    })


def test_validate_armor_recipe_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: name',
        'Missing required field: description',
        'Missing required field: location',
        'Missing required field: weight.center',
        'Missing required field: weight.radius',
        'Missing required field: defense.min.center',
        'Missing required field: defense.min.radius',
        'Missing required field: defense.max.center',
        'Missing required field: defense.max.radius'
    ]
    with pytest.raises(ValidationError) as e:
        armor.validate_recipe({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_armor_recipe_invalid_location():
    expected = 'Invalid armor location'
    with pytest.raises(ValidationError) as e:
        armor.validate_recipe({'location': 'foobar'})
    actual = e.value.errors
    assert expected in actual


def test_validate_armor_recipe_interval_values_negative():
    expected = [
        'Weight must be >= 0',
        'Min defense must be > 0',
        'Max defense must be > 0'
    ]
    with pytest.raises(ValidationError) as e:
        armor.validate_recipe({
            'weight': {'center': 5, 'radius': 10},
            'defense': {
                'min': {'center': 10, 'radius': 20},
                'max': {'center': 15, 'radius': 30}
            }
        })
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_armor_recipe_interval_values_zero():
    expected = [
        'Min defense must be > 0',
        'Max defense must be > 0'
    ]
    with pytest.raises(ValidationError) as e:
        armor.validate_recipe({
            'weight': {'center': 5, 'radius': 5},
            'defense': {
                'min': {'center': 10, 'radius': 10},
                'max': {'center': 15, 'radius': 15}
            }
        })
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_armor_recipe_max_defense_less_than_min_defense():
    expected = 'Min defense must be <= max defense for all values'
    with pytest.raises(ValidationError) as e:
        armor.validate_recipe({
            'defense': {
                'min': {'center': 20, 'radius': 5},
                'max': {'center': 10, 'radius': 5}
            }
        })
    actual = e.value.errors
    assert expected in actual


def test_validate_armor_recipe_min_defense_intersects_max_defense():
    expected = 'Min defense must be <= max defense for all values'
    with pytest.raises(ValidationError) as e:
        armor.validate_recipe({
            'defense': {
                'min': {'center': 90, 'radius': 10},
                'max': {'center': 100, 'radius': 25}
            }
        })
    actual = e.value.errors
    assert expected in actual


@patch('wtf.core.armor.find_recipe_by_id')
def test_validate_armor(mock_find_recipe_by_id):
    mock_find_recipe_by_id.return_value = 'foobar'
    armor.validate({
        'id': TEST_DATA['id'],
        'recipe': TEST_DATA['recipe']['id'],
        'grade': TEST_DATA['grade']
    })


def test_validate_armor_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: recipe',
        'Missing required field: grade'
    ]
    with pytest.raises(ValidationError) as e:
        armor.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


@patch('wtf.core.armor.find_recipe_by_id')
def test_validate_armor_recipe_not_found(mock_find_recipe_by_id):
    expected = 'Armor recipe not found'
    error = NotFoundError('Armor recipe not found')
    mock_find_recipe_by_id.side_effect = error
    with pytest.raises(ValidationError) as e:
        armor.validate({'recipe': 'foobar'})
    assert expected in e.value.errors


def test_validate_armor_grade_0_to_1():
    expected = 'Equipment grade must be >= 0.0 and <= 1.0'
    for grade in [-0.42, 1.42]:
        with pytest.raises(ValidationError) as e:
            armor.validate({'grade': grade})
        assert expected in e.value.errors


def test_find_armor_recipe_by_id():
    expected = {'id': TEST_DATA['recipe']['id']}
    armor.REPO_RECIPES['by_id'][expected['id']] = expected
    actual = armor.find_recipe_by_id(TEST_DATA['recipe']['id'])
    assert expected == actual


def test_find_armor_recipe_by_id_not_found():
    expected = 'Armor recipe not found'
    with pytest.raises(NotFoundError) as e:
        actual = armor.find_recipe_by_id(TEST_DATA['recipe']['id'])
    actual = str(e.value)
    assert expected == actual


def test_find_armor_by_id():
    expected = {'id': TEST_DATA['id']}
    armor.REPO['by_id'][expected['id']] = expected
    actual = armor.find_by_id(TEST_DATA['id'])
    assert expected == actual


def test_find_armor_by_id_not_found():
    expected = 'Armor not found'
    with pytest.raises(NotFoundError) as e:
        actual = armor.find_by_id(TEST_DATA['id'])
    actual = str(e.value)
    assert expected == actual


@pytest.mark.parametrize("name,description", [
    pytest.param(TEST_DATA['name'], TEST_DATA['description']),
    pytest.param(None, None)
])
@patch('wtf.core.armor.find_recipe_by_id')
def test_transform_weapon(mock_find_recipe_by_id, name, description):
    recipe = TEST_DATA.get('recipe')
    mock_find_recipe_by_id.return_value = recipe
    expected = {
        'recipe': recipe['id'],
        'name': recipe['name'] if not name else name,
        'description': (
            recipe['description'] if not description else description
        ),
        'location': recipe['location'],
        'grade': '+%s' % int(TEST_DATA['grade'] * 10),
        'weight': TEST_DATA['weight'],
        'defense': {
            'min': TEST_DATA['defense']['min'],
            'max': TEST_DATA['defense']['max']
        },
        'other': 'fields'
    }
    actual = armor.transform({
        'recipe': recipe['id'],
        'grade': TEST_DATA['grade'],
        'name': name,
        'description': description,
        'other': 'fields'
    })
    assert expected == actual
