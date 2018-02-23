# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import numpy as np
import pytest
from mock import Mock, patch
from wtf.core import weapons, weaponrecipes_test
from wtf.core.errors import NotFoundError, ValidationError


TEST_DATA = {
    'id': 'ebe3f790-a7da-447b-86b3-82efd7e52ff4',
    'recipe': weaponrecipes_test.TEST_DATA,
    'name': 'Universal Foo Sword',
    'description': 'The mightiest sword in all the universe.',
    'grade': 0.345,
    'grade_probabilities': {
        'default': [
            0.90000000009,
            0.090000000009,
            0.0090000000009,
            0.00090000000009,
            9.0000000009e-05,
            9.0000000009e-06,
            9.0000000009e-07,
            9.0000000009e-08,
            9.0000000009e-09,
            9.0000000009e-10
        ],
        "custom": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    },
    'weight': 12.93,
    'damage': {
        'min': 46.9,
        'max': 96.9
    }
}


def setup_function():
    weapons.REPO = {'by_id': {}}


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


@patch('wtf.core.weapons.generate_grade')
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


@pytest.mark.parametrize("random_value,probabilities", [
    pytest.param(0.042, TEST_DATA['grade_probabilities']['custom']),
    pytest.param(0.023, None)
])
@patch('wtf.core.weapons.np.random')
def test_generate_weapon_grade_(mock_np_random, random_value, probabilities):
    expected = TEST_DATA['grade']
    mock_np_random.uniform.return_value = random_value
    mock_np_random.choice.return_value = expected
    actual = weapons.generate_grade(probabilities)
    assert expected == actual
    args, kwargs = mock_np_random.choice.call_args_list[0]
    choices = np.array([[0.1 * i + random_value for i in range(10)]])
    assert np.all(np.array(args) == np.array([choices]))
    default_probabilities = TEST_DATA['grade_probabilities']['default']
    assert kwargs == {'p': probabilities or default_probabilities}


def test_weapon_grade_probabilities_default():
    expected = TEST_DATA['grade_probabilities']['default']
    actual = weapons.grade_probabilities()
    assert expected == actual


@pytest.mark.parametrize("name,description", [
    pytest.param(TEST_DATA['name'], TEST_DATA['description']),
    pytest.param(None, None)
])
@patch('wtf.core.weapons.weaponrecipes')
def test_transform_weapon(mock_weaponrecipes, name, description):
    recipe = TEST_DATA.get('recipe')
    mock_weaponrecipes.find_by_id = Mock(return_value=recipe)
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
        'other': 'fields',
        'name': name,
        'description': description
    })
    assert expected == actual


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


@patch('wtf.core.weapons.weaponrecipes')
def test_validate_weapon(mock_weaponrecipes):
    mock_weaponrecipes.find_by_id = Mock(return_value='foobar')
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


@patch('wtf.core.weapons.weaponrecipes')
def test_validate_weapon_recipe_not_found(mock_weaponrecipes):
    expected = 'Weapon recipe not found'
    mock_weaponrecipes.find_by_id = Mock(
        side_effect=NotFoundError('Weapon recipe not found')
    )
    with pytest.raises(ValidationError) as e:
        weapons.validate({'recipe': 'foobar'})
    assert expected in e.value.errors


def test_validate_weapon_grade_0_to_1():
    expected = 'Weapon grade must be between 0.0 and 1.0'
    for grade in [-0.42, 1.42]:
        with pytest.raises(ValidationError) as e:
            weapons.validate({'grade': grade})
        assert expected in e.value.errors


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
