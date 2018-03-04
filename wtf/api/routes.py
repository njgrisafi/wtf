'''
wtf.api.routes

API route handlers.
'''
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from wtf.core import accounts, armor, characters, weapons, messages
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


def get_query_args():
    '''Get the request query args.'''
    return request.args


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
            "name": "...",
            "description": "...",
            "weight": {
                "center": ...,
                "radius": ...
            },
            "type": "...",
            "handedness": ...,
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
    recipe = weapons.save_recipe(weapons.create_recipe(
        name=body.get('name'),
        description=body.get('description'),
        weight=dict(center=weight.get('center'), radius=weight.get('radius')),
        type=body.get('type'),
        handedness=body.get('handedness'),
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
    recipe = weapons.find_recipe_by_id(recipe_id)
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


@BLUEPRINT.route('/armor-recipes', methods=['POST'])
def create_armor_recipe():
    '''Create an armor recipe.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/armor-recipes \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "name": "...",
            "description": "...",
            "weight": {
                "center": ...,
                "radius": ...
            },
            "location": ...,
            "defense": {
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
    defense = body.get('defense', {})
    defense_min = defense.get('min', {})
    defense_max = defense.get('max', {})
    recipe = armor.save_recipe(armor.create_recipe(
        name=body.get('name'),
        description=body.get('description'),
        weight=dict(center=weight.get('center'), radius=weight.get('radius')),
        location=body.get('location'),
        defense=dict(
            min=dict(
                center=defense_min.get('center'),
                radius=defense_min.get('radius')
            ),
            max=dict(
                center=defense_max.get('center'),
                radius=defense_max.get('radius')
            )
        )
    ))
    return jsonify({'recipe': recipe}), 201


@BLUEPRINT.route('/armor-recipes/<recipe_id>', methods=['GET'])
def get_armor_recipe_by_id(recipe_id):
    '''Get an armor recipe by its ID.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/armor-recipes/<id> \
        --write-out "\n"
    '''
    recipe = armor.find_recipe_by_id(recipe_id)
    return jsonify({'recipe': recipe}), 200


@BLUEPRINT.route('/armor', methods=['POST'])
def create_armor():
    '''Create an armor.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/armor \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "recipe": "..."
        }'
    '''
    body = get_json_body()
    new_armor = armor.save(armor.create(
        recipe=body.get('recipe')
    ))
    return jsonify({'armor': armor.transform(new_armor)}), 201


@BLUEPRINT.route('/armor/<armor_id>', methods=['GET'])
def get_armor_by_id(armor_id):
    '''Get an armor by its ID.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/armor/<id> \
        --write-out "\n"
    '''
    existing_armor = armor.find_by_id(armor_id)
    return jsonify({'armor': armor.transform(existing_armor)}), 200


@BLUEPRINT.route('/messages', methods=['GET'])
def get_messages():
    '''Handle message retrieval by recipient id.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/messages?recipient=<recipient_id>&status=<status> \
        --write-out "\n"
    '''
    args = get_query_args()
    status = args.get('status')
    recipient = args.get('recipient')
    message_copies = messages.get_recipient_message_copies(recipient=recipient, status=status)
    return jsonify({'messages': messages.transform_copies(message_copies)}), 200


@BLUEPRINT.route('/messages', methods=['POST'])
def create_message():
    '''Handle message creation requests.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/messages \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "subject": "...",
            "body": "...",
            "recipients": ["..."],
        }'
    '''
    body = get_json_body()
    message = messages.save(messages.create(
        subject=body.get('subject'),
        body=body.get('body'),
        recipients=body.get('recipients')
    ))
    return jsonify({'message': message}), 201


@BLUEPRINT.route('/messages/<message_id>', methods=['GET'])
def get_message_by_id(message_id):
    '''Handle message retrieval by ID requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/messages/<message_id> \
        --write-out "\n"
    '''
    message = messages.find_by_id(message_id)
    return jsonify({'message': messages.transform(message)}), 200


@BLUEPRINT.route('/messages/<message_id>/replies', methods=['POST'])
def create_message_reply(message_id):
    '''Handle reply for message by message id.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/messages/<message_id>/replies \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "subject": "...",
            "body": "...",
            "recipients": ["..."],
        }'
    '''
    messages.find_by_id(message_id)
    body = get_json_body()
    message = messages.save(messages.create(
        subject=body.get('subject'),
        body=body.get('body'),
        recipients=body.get('recipients'),
        parent=message_id
    ))
    return jsonify({'message': messages.transform(message)}), 201


@BLUEPRINT.route('/messages/<message_id>/replies', methods=['GET'])
def get_message_replies(message_id):
    '''Gets replies for a message.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/messages/<message_id>/replies \
        --write-out "\n"
    '''
    message_replies = messages.find_by_parent(message_id)
    message_replies = list(map(lambda m: messages.transform(m), message_replies))
    return jsonify({'replies': message_replies}), 200
