'''
wtf.api.routes

API route handlers.
'''
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from wtf.core import accounts, characters, weaponrecipes, weapons
from wtf.core.errors import NotFoundError, ValidationError


BLUEPRINT = Blueprint('api', __name__)


def get_json_body():
    '''Get the JSON request body.'''
    body = None
    if request.content_type != 'application/json':
        raise ValidationError('Content-Type header must be: application/json')
    else:
        try:
            body = request.get_json()
        except BadRequest:
            raise ValidationError('Unable to parse JSON request body')
    return body


@BLUEPRINT.errorhandler(ValidationError)
def handle_invalid_request(error):
    '''Handle ValidationError errors.'''
    return jsonify({'errors': error.errors}), 400


@BLUEPRINT.errorhandler(NotFoundError)
def handle_not_found(error):
    '''Handle NotFoundError errors.'''
    return jsonify({'errors': [str(error)]}), 404


# pylint: disable=unused-argument
@BLUEPRINT.errorhandler(Exception)
def handle_error(error):
    '''Handle errors not caught by another error handler.'''
    return jsonify({'errors': ['Internal Server Error']}), 500


@BLUEPRINT.route('/health', methods=['GET'])
def get_health():
    '''Check the health of the API.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/health \
        --write-out "\n"
    '''
    return 'Healthy'


@BLUEPRINT.route('/accounts', methods=['POST'])
def create_account():
    '''Create an account.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/accounts \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "email": "...",
            "password": "..."
        }'
    '''
    body = get_json_body()
    account = accounts.save(accounts.create(
        email=body.get('email'),
        password=body.get('password')
    ))
    return jsonify({'account': accounts.transform(account)}), 201


@BLUEPRINT.route('/accounts/<account_id>', methods=['GET'])
def get_account_by_id(account_id):
    '''Get an account by its ID.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/accounts/<id> \
        --write-out "\n"
    '''
    account = accounts.find_by_id(account_id)
    return jsonify({'account': accounts.transform(account)}), 200


@BLUEPRINT.route('/characters', methods=['POST'])
def create_character():
    '''Create a character.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/characters \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "account": "...",
            "name": "..."
        }'
    '''
    body = get_json_body()
    character = characters.save(characters.create(
        account=body.get('account'),
        name=body.get('name')
    ))
    return jsonify({'character': character}), 201


@BLUEPRINT.route('/characters/<character_id>', methods=['GET'])
def get_character_by_id(character_id):
    '''Find a character by its ID.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/characters/<id> \
        --write-out "\n"
    '''
    character = characters.find_by_id(character_id)
    return jsonify({'character': character}), 200


@BLUEPRINT.route('/weapon-recipes', methods=['POST'])
def create_weapon_recipe():
    '''Create a weapon recipe.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/weapon-recipes \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "type": "...",
            "name": "...",
            "description": "...",
            "handedness": ...,
            "weight": {
                "center": ...,
                "radius": ...
            },
            "damage": {
                "min": {
                    "center": ...,
                    "radius": ...
                },
                "max": {
                    "center": ...,
                    "radius": ...
                }
            }
        }'
    '''
    body = get_json_body()
    weight = body.get('weight', {})
    damage = body.get('damage', {})
    damage_min = damage.get('min', {})
    damage_max = damage.get('max', {})
    recipe = weaponrecipes.save(weaponrecipes.create(
        type=body.get('type'),
        name=body.get('name'),
        description=body.get('description'),
        handedness=body.get('handedness'),
        weight=dict(center=weight.get('center'), radius=weight.get('radius')),
        damage=dict(
            min=dict(
                center=damage_min.get('center'),
                radius=damage_min.get('radius')
            ),
            max=dict(
                center=damage_max.get('center'),
                radius=damage_max.get('radius')
            )
        )
    ))
    return jsonify({'recipe': recipe}), 201


@BLUEPRINT.route('/weapon-recipes/<recipe_id>', methods=['GET'])
def get_weapon_recipe_by_id(recipe_id):
    '''Get a weapon recipe by its ID.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/weapon-recipes/<id> \
        --write-out "\n"
    '''
    recipe = weaponrecipes.find_by_id(recipe_id)
    return jsonify({'recipe': recipe}), 200


@BLUEPRINT.route('/weapons', methods=['POST'])
def create_weapon():
    '''Create a weapon.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/weapons \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "recipe": "..."
        }'
    '''
    body = get_json_body()
    weapon = weapons.save(weapons.create(
        recipe=body.get('recipe')
    ))
    return jsonify({'weapon': weapons.transform(weapon)}), 201


@BLUEPRINT.route('/weapons/<weapon_id>', methods=['GET'])
def get_weapon_by_id(weapon_id):
    '''Get a weapon by its ID.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/weapons/<id> \
        --write-out "\n"
    '''
    weapon = weapons.find_by_id(weapon_id)
    return jsonify({'weapon': weapons.transform(weapon)}), 200
