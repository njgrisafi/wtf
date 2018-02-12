# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from wtf.api import weaponrecipes
from wtf.api.errors import ValidationError


def test_validate_weapon_recipe():
    weaponrecipes.validate({
        'type': 'sword',
        'name': 'Foo Sword',
        'description': 'The mightiest sword in all the land.',
        'handedness': 2,
        'weight': {'center': 12, 'radius': 3},
        'damage': {
            'min': {'center': 50, 'radius': 10},
            'max': {'center': 100, 'radius': 10}
        }
    })


def test_validate_weapon_recipe_missing_fields():
    expected = [
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
    assert set(expected).issubset(e.value.errors)


def test_validate_weapon_recipe_invalid_type():
    expected = 'Invalid weapon type'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({'type': 'foobar'})
    assert expected in e.value.errors


def test_validate_weapon_recipe_invalid_handedness():
    expected = 'Handedness must be either 1 or 2'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({'handedness': 42})
    assert expected in e.value.errors


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
    assert set(expected).issubset(e.value.errors)


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
    assert set(expected).issubset(e.value.errors)


def test_validate_weapon_recipe_max_damage_less_than_min_damage():
    expected = 'Min damage must always be less than max damage'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({
            'damage': {
                'min': {'center': 20, 'radius': 5},
                'max': {'center': 10, 'radius': 5}
            }
        })
    assert expected in e.value.errors


def test_validate_weapon_recipe_min_damage_intersects_max_damage():
    expected = 'Min damage must always be less than max damage'
    with pytest.raises(ValidationError) as e:
        weaponrecipes.validate({
            'damage': {
                'min': {'center': 90, 'radius': 10},
                'max': {'center': 100, 'radius': 25}
            }
        })
    assert expected in e.value.errors


def test_create_weapon_recipe():
    expected = {
        'type': 'sword',
        'name': 'Foo Sword',
        'description': 'The mightiest sword in all the land.',
        'handedness': 2,
        'weight': {'center': 12, 'radius': 3},
        'damage': {
            'min': {'center': 45, 'radius': 6},
            'max': {'center': 78, 'radius': 9}
        }
    }
    actual = weaponrecipes.create(
        type='sword',
        name='Foo Sword',
        description='The mightiest sword in all the land.',
        handedness=2,
        weight=dict(center=12, radius=3),
        damage=dict(
            min=dict(center=45, radius=6),
            max=dict(center=78, radius=9)
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
