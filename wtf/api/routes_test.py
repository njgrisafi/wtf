# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch, Mock
from werkzeug.exceptions import BadRequest
from wtf.api import routes
from wtf.api.app import create_app
from wtf.core.errors import NotFoundError, ValidationError
from wtf.testing import create_test_client


TEST_DATA = {
    'account': {'id': '270e6e8a-ea43-4859-98cc-09d5dd381679'},
    'character': {'id': '7d700f0e-c25d-4bba-a9de-d5e79d0eeebe'},
    'weapon_recipe': {'id': '2513cb35-9a34-4612-8541-4916035979f3'},
    'weapon': {'id': 'ebe3f790-a7da-447b-86b3-82efd7e52ff4'},
    'armor_recipe': {'id': '31c87b87-6f6b-49d5-a095-e9f71abe7def'},
    'armor': {'id': '29b2f4d9-67f6-4061-85dd-cd5d6ec02bb8'},
    'message': {'id': '0a0b0c0d-0e0f-0a0b-0c0d-0e0f0a0b0c0d'}
}


@pytest.fixture
def test_client():
    client = create_test_client(create_app())
    client.set_root_path('/api')
    client.set_default_headers({'Content-Type': 'application/json'})
    return client


@patch('wtf.api.routes.request')
def test_get_json_body(mock_request):
    expected = {'foo': 'bar'}
    mock_request.content_type = 'application/json'
    mock_request.get_json = Mock(return_value=expected)
    actual = routes.get_json_body()
    assert expected == actual


@patch('wtf.api.routes.request')
def test_get_json_body_content_type_not_json(mock_request):
    expected = 'Content-Type header must be: application/json'
    mock_request.content_type = 'application/html'
    with pytest.raises(ValidationError) as e:
        routes.get_json_body()
    actual = e.value.errors
    assert expected in actual


@patch('wtf.api.routes.request')
def test_get_json_body_invalid(mock_request):
    expected = 'Unable to parse JSON request body'
    mock_request.content_type = 'application/json'
    mock_request.get_json = Mock(side_effect=BadRequest())
    with pytest.raises(ValidationError) as e:
        routes.get_json_body()
    actual = e.value.errors
    assert expected in actual


@patch('wtf.api.routes.jsonify')
def test_handle_invalid_request_error(mock_jsonify):
    mock_jsonify.side_effect = lambda b: b
    error = ValidationError(errors=['foo', 'bar', 'baz'])
    response, status_code = routes.handle_invalid_request(error)
    assert response == {'errors': ['foo', 'bar', 'baz']}
    assert status_code == 400


@patch('wtf.api.routes.jsonify')
def test_handle_not_found_error(mock_jsonify):
    mock_jsonify.side_effect = lambda b: b
    error = NotFoundError('Foobar not found')
    response, status_code = routes.handle_not_found(error)
    assert response == {'errors': ['Foobar not found']}
    assert status_code == 404


@patch('wtf.api.routes.jsonify')
def test_handle_misc_error(mock_jsonify):
    mock_jsonify.side_effect = lambda b: b
    error = Exception('foo bar baz')
    response, status_code = routes.handle_error(error)
    assert response == {'errors': ['Internal Server Error']}
    assert status_code == 500


def test_get_health(test_client):
    response = test_client.get('/health')
    response.assert_status_code(200)
    response.assert_body(b'Healthy')


@patch('wtf.core.accounts.transform')
@patch('wtf.core.accounts.save')
def test_create_account(mock_save, mock_transform, test_client):
    mock_save.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.post('/accounts', body={})
    response.assert_status_code(201)
    response.assert_body({'account': 'foobar-transformed'})


@patch('wtf.core.accounts.save')
def test_create_account_invalid(mock_save, test_client):
    mock_save.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post('/accounts', body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.core.accounts.find_by_id')
def test_get_account_by_id(mock_find_by_id, test_client):
    mock_find_by_id.return_value = {'foo': 'bar', 'password': 'foobar'}
    for _ in range(2):
        response = test_client.get('/accounts/%s' % TEST_DATA['account']['id'])
        response.assert_status_code(200)
        response.assert_body({'account': {'foo': 'bar'}})


def test_get_account_by_id_not_found(test_client):
    response = test_client.get('/accounts/%s' % TEST_DATA['account']['id'])
    response.assert_status_code(404)
    response.assert_body({'errors': ['Account not found']})


@patch('wtf.core.characters.save')
def test_create_character(mock_save, test_client):
    mock_save.return_value = 'foobar'
    response = test_client.post('/characters', body={})
    response.assert_status_code(201)
    response.assert_body({'character': 'foobar'})


@patch('wtf.core.characters.save')
def test_create_character_invalid(mock_save, test_client):
    mock_save.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post('/characters', body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.core.characters.find_by_id')
def test_get_character_by_id(mock_find_by_id, test_client):
    mock_find_by_id.return_value = 'foobar'
    response = test_client.get('/characters/%s' % TEST_DATA['character']['id'])
    response.assert_status_code(200)
    response.assert_body({'character': 'foobar'})


def test_get_character_by_id_not_found(test_client):
    response = test_client.get('/characters/%s' % TEST_DATA['character']['id'])
    response.assert_status_code(404)
    response.assert_body({'errors': ['Character not found']})


@patch('wtf.core.weapons.save_recipe')
def test_create_weapon_recipe(mock_save_recipe, test_client):
    mock_save_recipe.return_value = 'foobar'
    response = test_client.post('/weapon-recipes', body={})
    response.assert_status_code(201)
    response.assert_body({'recipe': 'foobar'})


@patch('wtf.core.weapons.save_recipe')
def test_create_weapon_recipe_invalid(mock_save_recipe, test_client):
    mock_save_recipe.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post('/weapon-recipes', body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.core.weapons.find_recipe_by_id')
def test_get_weapon_recipe_by_id(mock_find_recipe_by_id, test_client):
    mock_find_recipe_by_id.return_value = 'foobar'
    recipe_id = TEST_DATA['weapon_recipe']['id']
    response = test_client.get('/weapon-recipes/%s' % recipe_id)
    response.assert_status_code(200)
    response.assert_body({'recipe': 'foobar'})


def test_get_weapon_recipe_by_id_not_found(test_client):
    recipe_id = TEST_DATA['weapon_recipe']['id']
    response = test_client.get('/weapon-recipes/%s' % recipe_id)
    response.assert_status_code(404)
    response.assert_body({'errors': ['Weapon recipe not found']})


@patch('wtf.core.weapons.transform')
@patch('wtf.core.weapons.save')
def test_create_weapon(mock_save, mock_transform, test_client):
    mock_save.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.post('/weapons', body={})
    response.assert_status_code(201)
    response.assert_body({'weapon': 'foobar-transformed'})


@patch('wtf.core.weapons.save')
def test_create_weapon_invalid(mock_save, test_client):
    mock_save.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post('/weapons', body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.core.weapons.transform')
@patch('wtf.core.weapons.find_by_id')
def test_get_weapon_by_id(mock_find_by_id, mock_transform, test_client):
    mock_find_by_id.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.get('/weapons/%s' % TEST_DATA['weapon']['id'])
    response.assert_status_code(200)
    response.assert_body({'weapon': 'foobar-transformed'})


def test_get_weapon_by_id_not_found(test_client):
    response = test_client.get('/weapons/%s' % TEST_DATA['weapon']['id'])
    response.assert_status_code(404)
    response.assert_body({'errors': ['Weapon not found']})


@patch('wtf.core.armor.save_recipe')
def test_create_armor_recipe(mock_save_recipe, test_client):
    mock_save_recipe.return_value = 'foobar'
    response = test_client.post('/armor-recipes', body={})
    response.assert_status_code(201)
    response.assert_body({'recipe': 'foobar'})


@patch('wtf.core.armor.save_recipe')
def test_create_armor_recipe_invalid(mock_save_recipe, test_client):
    mock_save_recipe.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post('/armor-recipes', body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.core.armor.find_recipe_by_id')
def test_get_armor_recipe_by_id(mock_find_recipe_by_id, test_client):
    mock_find_recipe_by_id.return_value = 'foobar'
    recipe_id = TEST_DATA['armor_recipe']['id']
    response = test_client.get('/armor-recipes/%s' % recipe_id)
    response.assert_status_code(200)
    response.assert_body({'recipe': 'foobar'})


def test_get_armor_recipe_by_id_not_found(test_client):
    recipe_id = TEST_DATA['armor_recipe']['id']
    response = test_client.get('/armor-recipes/%s' % recipe_id)
    response.assert_status_code(404)
    response.assert_body({'errors': ['Armor recipe not found']})


@patch('wtf.core.armor.transform')
@patch('wtf.core.armor.save')
def test_create_armor(mock_save, mock_transform, test_client):
    mock_save.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.post('/armor', body={})
    response.assert_status_code(201)
    response.assert_body({'armor': 'foobar-transformed'})


@patch('wtf.core.armor.save')
def test_create_armor_invalid(mock_save, test_client):
    mock_save.side_effect = ValidationError(errors=['foo', 'bar', 'baz'])
    response = test_client.post('/armor', body={})
    response.assert_status_code(400)
    response.assert_body({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.core.armor.transform')
@patch('wtf.core.armor.find_by_id')
def test_get_armor_by_id(mock_find_by_id, mock_transform, test_client):
    mock_find_by_id.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.get('/armor/%s' % TEST_DATA['armor']['id'])
    response.assert_status_code(200)
    response.assert_body({'armor': 'foobar-transformed'})


def test_get_armor_by_id_not_found(test_client):
    response = test_client.get('/armor/%s' % TEST_DATA['armor']['id'])
    response.assert_status_code(404)
    response.assert_body({'errors': ['Armor not found']})


@patch('wtf.core.messages.save')
def test_create_message(
        mock_save,
        test_client
    ):
    expected = 'foobar'
    mock_save.return_value = expected
    response = test_client.post('/messages', body={})
    response.assert_status_code(201)
    response.assert_body({'message': 'foobar'})


@patch('wtf.core.messages.transform')
@patch('wtf.core.messages.save')
@patch('wtf.core.messages.find_by_id')
def test_create_message_reply(
        mock_save,
        mock_find_by_id,
        mock_transform,
        test_client
    ):
    mock_save.return_value = 'foobar'
    mock_find_by_id.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.post('/messages/%s/replies' % TEST_DATA['message']['id'],
                                body={'body': 'test', 'subject': 'test', 'recipients': ['test']}
                               )
    response.assert_status_code(201)
    response.assert_body({'message': 'foobar-transformed'})

@patch('wtf.core.messages.transform')
@patch('wtf.core.messages.find_by_id')
def test_get_message_by_id(
        mock_find_by_id,
        mock_transform,
        test_client
    ):
    mock_find_by_id.return_value = 'foobar'
    mock_transform.return_value = 'foobar-transformed'
    for _ in range(2):
        response = test_client.get('/messages/%s' % TEST_DATA['message']['id'])
        response.assert_status_code(200)
        response.assert_body({'message': 'foobar-transformed'})


@patch('wtf.core.messages.transform_copies')
@patch('wtf.core.messages.get_recipient_message_copies')
def test_get_messages(
        mock_get_recipient_message_copies,
        mock_transform_copies,
        test_client
    ):
    mock_get_recipient_message_copies.return_value = 'foobar'
    mock_transform_copies.return_value = 'foobar-transformed'
    response = test_client.get('/messages',
                               query_string={'recipient': 'test'}
                              )
    response.assert_status_code(200)
    response.assert_body({'messages': 'foobar-transformed'})


@patch('wtf.core.messages.transform')
@patch('wtf.core.messages.find_by_parent')
def test_get_message_replies(
        mock_find_by_parent,
        mock_transform,
        test_client
    ):
    mock_find_by_parent.return_value = ['foobar']
    mock_transform.return_value = 'foobar-transformed'
    response = test_client.get('/messages/%s/replies' % TEST_DATA['message']['id'])
    response.assert_status_code(200)
    response.assert_body({'replies': ['foobar-transformed']})
