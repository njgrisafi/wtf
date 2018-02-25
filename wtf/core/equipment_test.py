# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import numpy as np
import pytest
from mock import patch
from wtf.core import equipment
from wtf.core.errors import ValidationError


TEST_DATA = {
    'id': 'b4a72355-a32d-468e-b92c-5820e3a49e0b',
    'name': 'Awesome Foo Thing',
    'description': 'The awesomest thing in all existence.',
    'recipe': {
        'id': 'da72c040-aeb4-42e2-8782-42e62c20971d',
        'name': 'Foo Thing',
        'description': 'The mightiest thing in all the land.',
        'weight': {'center': 12.3, 'radius': 4.5},
        'foo': {
            'min': {'center': 10, 'radius': 3},
            'max': {'center': 20, 'radius': 5}
        }
    },
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
    'grade': 0.123,
    'grade_transformed': '+1',
    'weight': 15.69
}


def test_create_equipment_recipe():
    recipe = TEST_DATA['recipe']
    expected = {
        'name': TEST_DATA['name'],
        'description': TEST_DATA['description'],
        'weight': recipe['weight']
    }
    actual = equipment.create_recipe(
        name=TEST_DATA['name'],
        description=TEST_DATA['description'],
        weight=dict(
            center=recipe['weight']['center'],
            radius=recipe['weight']['radius']
        )
    )
    assert expected == actual


def test_create_equipment_recipe_defaults():
    expected = {
        'name': None,
        'description': None,
        'weight': {
            'center': None,
            'radius': None
        }
    }
    actual = equipment.create_recipe()
    assert expected == actual


def test_create_equipment():
    expected = {
        'recipe': TEST_DATA['recipe']['id'],
        'name': TEST_DATA['name'],
        'description': TEST_DATA['description'],
        'grade': TEST_DATA['grade']
    }
    actual = equipment.create(
        recipe=TEST_DATA['recipe']['id'],
        name=TEST_DATA['name'],
        description=TEST_DATA['description'],
        grade=TEST_DATA['grade']
    )
    assert expected == actual


@patch('wtf.core.equipment.generate_grade')
def test_create_equipment_defaults(mock_generate_grade):
    mock_generate_grade.return_value = TEST_DATA['grade']
    expected = {
        'recipe': None,
        'name': None,
        'description': None,
        'grade': TEST_DATA['grade']
    }
    actual = equipment.create()
    assert expected == actual


@pytest.mark.parametrize("random_value,probabilities", [
    pytest.param(0.042, TEST_DATA['grade_probabilities']['custom']),
    pytest.param(0.023, None)
])
@patch('wtf.core.equipment.np.random')
def test_generate_equipment_grade(mock_np_random, random_value, probabilities):
    expected = TEST_DATA['grade']
    mock_np_random.uniform.return_value = random_value
    mock_np_random.choice.return_value = expected
    actual = equipment.generate_grade(probabilities)
    assert expected == actual
    args, kwargs = mock_np_random.choice.call_args_list[0]
    choices = np.array([[0.1 * i + random_value for i in range(10)]])
    assert np.all(np.array(args) == np.array([choices]))
    default_probabilities = TEST_DATA['grade_probabilities']['default']
    assert kwargs == {'p': probabilities or default_probabilities}


def test_equipment_grade_probabilities_default():
    expected = TEST_DATA['grade_probabilities']['default']
    actual = equipment.grade_probabilities()
    assert expected == actual


def test_validate_equipment_recipe():
    equipment.validate_recipe(TEST_DATA['recipe'])


def test_validate_equipment_recipe_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: name',
        'Missing required field: description',
        'Missing required field: weight.center',
        'Missing required field: weight.radius'
    ]
    with pytest.raises(ValidationError) as e:
        equipment.validate_recipe({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_equipment_recipe_weight_negative():
    expected = 'Weight must be >= 0'
    with pytest.raises(ValidationError) as e:
        equipment.validate_recipe({
            'weight': {
                'center': 0,
                'radius': 5
            }
        })
    actual = e.value.errors
    assert expected in actual


def test_validate_equipment_recipe_min_max_field():
    equipment.validate_recipe_min_max_field(TEST_DATA['recipe'], 'foo')


def test_validate_equipment_recipe_min_max_field_missing_fields():
    expected = [
        'Missing required field: foo.min.center',
        'Missing required field: foo.min.radius',
        'Missing required field: foo.max.center',
        'Missing required field: foo.max.radius'
    ]
    with pytest.raises(ValidationError) as e:
        equipment.validate_recipe_min_max_field({}, 'foo')
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_equipment_recipe_min_max_field_zero():
    expected = ['Min foo must be > 0', 'Max foo must be > 0']
    with pytest.raises(ValidationError) as e:
        equipment.validate_recipe_min_max_field(
            recipe={
                'foo': {
                    'min': {'center': 1, 'radius': 1},
                    'max': {'center': 2, 'radius': 2},
                }
            },
            field_name='foo'
        )
    actual = e.value.errors
    assert set(expected).issubset(actual)


def test_validate_equipment_recipe_min_max_field_min_lte_max():
    expected = 'Min foo must be <= max foo for all values'
    with pytest.raises(ValidationError) as e:
        equipment.validate_recipe_min_max_field(
            recipe={
                'foo': {
                    'min': {'center': 5, 'radius': 2},
                    'max': {'center': 10, 'radius': 10},
                }
            },
            field_name='foo'
        )
    actual = e.value.errors
    assert expected in actual


def test_validate_equipment():
    equipment.validate({
        'id': TEST_DATA['id'],
        'grade': TEST_DATA['grade']
    })


def test_validate_equipment_missing_fields():
    expected = [
        'Missing required field: id',
        'Missing required field: grade'
    ]
    with pytest.raises(ValidationError) as e:
        equipment.validate({})
    actual = e.value.errors
    assert set(expected).issubset(actual)


@pytest.mark.parametrize("grade", [pytest.param(-0.42), pytest.param(1.42)])
def test_validate_equipment_grade_0_to_1(grade):
    expected = 'Equipment grade must be >= 0.0 and <= 1.0'
    with pytest.raises(ValidationError) as e:
        equipment.validate({'grade': grade})
    actual = e.value.errors
    assert expected in actual


def test_transform_equipment():
    recipe = TEST_DATA['recipe']
    expected = {
        'name': recipe['name'],
        'description': recipe['description'],
        'grade': TEST_DATA['grade_transformed'],
        'weight': TEST_DATA['weight']
    }
    actual = equipment.transform(
        equipment={
            'name': None,
            'description': None,
            'grade': TEST_DATA['grade']
        },
        recipe=recipe
    )
    assert expected == actual
