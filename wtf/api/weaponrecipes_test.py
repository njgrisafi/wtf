# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import weaponrecipes
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


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


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/weapon-recipes')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.weaponrecipes.save')
def test_handle_post_weapon_recipe_request(mock_save, test_client):
    expected = 'foobar'
    mock_save.return_value = 'foobar'
    response = test_client.post(
        body={
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
    )
    response.assert_status_code(201)
    response.assert_body(expected)


def test_handle_post_weapon_recipe_request_content_type_not_json(test_client):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body({
        'errors': ['Content-Type header must be: application/json']
    })


def test_handle_get_weapon_recipe_by_id_request(test_client):
    expected = {'recipe': {'foo': 'bar'}}
    by_id = weaponrecipes.REPO['by_id']
    by_id[TEST_DATA['id']] = {'foo': 'bar'}
    response = test_client.get(path='/%s' % TEST_DATA['id'])
    response.assert_status_code(200)
    response.assert_body(expected)


def test_handle_get_weapon_recipe_by_id_request_not_found(test_client):
    expected = {'errors': ['Weapon recipe not found']}
    response = test_client.get(path='/%s' % TEST_DATA['id'])
    response.assert_status_code(404)
    response.assert_body(expected)


@patch('wtf.api.weaponrecipes.uuid4')
@patch('wtf.api.weaponrecipes.validate')
def test_save_weapon_recipe_insert(mock_validate, mock_uuid4):
    expected = {'id': TEST_DATA['id']}
    mock_validate.return_value = None
    mock_uuid4.return_value = TEST_DATA['id']
    by_id = weaponrecipes.REPO['by_id']
    actual = weaponrecipes.save({'id': None})
    assert expected == actual
    assert expected == by_id[TEST_DATA['id']]


@patch('wtf.api.weaponrecipes.validate')
def test_save_weapon_recipe_update(mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_validate.return_value = None
    by_id = weaponrecipes.REPO['by_id']
    by_id[TEST_DATA['id']] = expected
    actual = weaponrecipes.save({'id': TEST_DATA['id']})
    assert expected == actual
    assert expected == by_id[TEST_DATA['id']]


def test_validate_weapon_recipe():
    weaponrecipes.validate({
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


def test_find_weapon_recipe_by_id():
    expected = 'foobar'
    by_id = weaponrecipes.REPO['by_id']
    by_id[TEST_DATA['id']] = expected
    assert weaponrecipes.find_by_id(TEST_DATA['id']) == expected


def test_find_weapon_recipe_by_id_not_found():
    with pytest.raises(NotFoundError) as e:
        weaponrecipes.find_by_id('foobar')
    assert str(e.value) == 'Weapon recipe not found'


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
