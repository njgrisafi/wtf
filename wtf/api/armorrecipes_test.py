# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
from wtf.api import armorrecipes


def test_armorrecipes_create():
    expected = {
        'name': 'foobar',
        'description': 'foo bar baz',
        'weight': {'center': 12, 'radius': 3},
        'defense': {
            'min': {'center': 45, 'radius': 6},
            'max': {'center': 78, 'radius': 9}
        }
    }
    actual = armorrecipes.create(
        name='foobar',
        description='foo bar baz',
        weight=dict(center=12, radius=3),
        defense=dict(
            min=dict(center=45, radius=6),
            max=dict(center=78, radius=9)
        )
    )
    assert expected == actual


def test_armorrecipes_create_defaults():
    expected = {
        'name': None,
        'description': None,
        'weight': {'center': 0, 'radius': 0},
        'defense': {
            'min': {'center': 0, 'radius': 0},
            'max': {'center': 0, 'radius': 0}
        }
    }
    actual = armorrecipes.create()
    assert expected == actual
