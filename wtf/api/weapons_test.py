# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import Mock, patch
from wtf.api import weapons, weaponrecipes_test
from wtf.api.app import create_app
from wtf.api.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


TEST_DATA = {
    'id': 'ebe3f790-a7da-447b-86b3-82efd7e52ff4',
    'recipe': weaponrecipes_test.TEST_DATA,
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
    weapons.REPO = {'by_id': {}}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api/weapons')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.weapons.derive')
@patch('wtf.api.weapons.save')
def test_handle_post_weapon_request(mock_save, mock_derive, test_client):
    mock_save.return_value = 'foobar'
    mock_derive.return_value = 'foobar-derived'
    response = test_client.post()
    response.assert_status_code(201)
    response.assert_body({'weapon': 'foobar-derived'})


@patch('wtf.api.weapons.save')
def test_handle_post_weapon_request_content_type_not_json(
        mock_save,
        test_client
    ):
    response = test_client.post(headers={'Content-Type': 'text/html'})
    response.assert_status_code(400)
    response.assert_body(
        {'errors': ['Content-Type header must be: application/json']}
    )
    mock_save.assert_not_called()


@patch('wtf.api.weapons.save')
def test_handle_post_weapon_request_invalid(mock_save, test_client):
    mock_save.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post()
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.api.weapons.derive')
@patch('wtf.api.weapons.find_by_id')
def test_handle_get_weapon_by_id_request(
        mock_find_by_id,
        mock_derive,
        test_client
    ):
    mock_find_by_id.return_value = 'foobar'
    mock_derive.return_value = 'foobar-derived'
    response = test_client.get(path='/%s' % TEST_DATA['id'])
    response.assert_status_code(200)
    response.assert_body({'weapon': 'foobar-derived'})


def test_handle_get_weapon_by_id_request_not_found(test_client):
    response = test_client.get(path='/%s' % TEST_DATA['id'])
    response.assert_status_code(404)
    response.assert_body({'errors': ['Weapon not found']})


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


@patch('wtf.api.weapons.generate_grade')
def test_create_weapon_defaults(mock_generate_grade):
    mock_generate_grade.return_value = 0.123
    expected = {
        'recipe': None,
        'name': None,
        'description': None,
        'grade': 0.123
    }
    actual = weapons.create()
    assert expected == actual



@pytest.mark.parametrize("name,description", [
    pytest.param(TEST_DATA['name'], TEST_DATA['description']),
    pytest.param(None, None)
])
@patch('wtf.api.weapons.weaponrecipes')
def test_derive_weapon(mock_weaponrecipes, name, description):
    recipe = TEST_DATA.get('recipe')
    mock_weaponrecipes.find_by_id = Mock(return_value=recipe)
    expected = {
        'name': recipe['name'] if not name else name,
        'description': (
            recipe['description'] if not description else description
        ),
        'recipe': recipe['id'],
        'grade': '+%s' % int(TEST_DATA['grade'] * 10),
        'weight': TEST_DATA['weight'],
        'damage': {
            'min': TEST_DATA['damage']['min'],
            'max': TEST_DATA['damage']['max']
        },
        'other': 'fields'
    }
    actual = weapons.derive({
        'recipe': recipe['id'],
        'grade': TEST_DATA['grade'],
        'other': 'fields',
        'name': name,
        'description': description
    })
    assert expected == actual


@patch('wtf.api.weapons.validate')
@patch('wtf.api.weapons.uuid4')
def test_save_weapon_insert(mock_uuid4, mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_uuid4.return_value = TEST_DATA['id']
    mock_validate.return_value = None
    actual = weapons.save({})
    assert expected == actual
    assert expected == weapons.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.api.weapons.validate')
def test_save_weapon_update(mock_validate):
    expected = {'id': TEST_DATA['id']}
    mock_validate.return_value = None
    actual = weapons.save({'id': TEST_DATA['id']})
    assert expected == actual
    assert expected == weapons.REPO['by_id'][TEST_DATA['id']]


@patch('wtf.api.weapons.validate')
def test_save_weapon_invalid(mock_validate):
    mock_validate.side_effect = ValidationError()
    with pytest.raises(ValidationError):
        weapons.save({})
    assert not weapons.REPO['by_id'].values()


@patch('wtf.api.weapons.weaponrecipes')
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


@patch('wtf.api.weapons.weaponrecipes')
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
