# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
from wtf.api import weapons


def test_weapons_create():
    expected = {
        'recipe': 'd2e0c2df-cacf-4bf7-bda0-fc5413b5d8b2',
        'type': 'sword',
        'name': 'Universal Foo Sword',
        'description': 'The mightiest sword in all the universe.',
        'grade': 0.345
    }
    actual = weapons.create(
        recipe='d2e0c2df-cacf-4bf7-bda0-fc5413b5d8b2',
        type='sword',
        name='Universal Foo Sword',
        description='The mightiest sword in all the universe.',
        grade=0.345
    )
    assert expected == actual


def test_weapons_create_defaults():
    expected = {
        'recipe': None,
        'name': None,
        'description': None,
        'type': None,
        'grade': 0.0
    }
    actual = weapons.create()
    assert expected == actual
