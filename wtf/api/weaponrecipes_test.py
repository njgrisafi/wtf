# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
from wtf.api import weaponrecipes


def test_weaponrecipes_create():
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


def test_weaponrecipes_create_defaults():
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
