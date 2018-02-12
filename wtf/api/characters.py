'''
wtf.api.characters

Routes and functions for manipulating characters.
'''
from uuid import uuid4
from flask import Blueprint, jsonify, request
from wtf.api import util
from wtf.api.errors import NotFoundError, ValidationError


BLUEPRINT = Blueprint('characters', __name__)
REPO_CHARACTERS = {
    'by_id': {},
    'by_account': {}
}


@BLUEPRINT.route('', methods=['POST'])
def handle_create_request():
    '''Handle character creation requests.

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
    util.validate_request(content_type='application/json')
    body = request.get_json(silent=True) or {}
    character = save(create(
        account=body.get('account'),
        name=body.get('name')
    ))
    return jsonify(character), 200


@BLUEPRINT.route('/<character_id>', methods=['GET'])
def handle_get_by_id_request(character_id):
    '''Handle character retrieval by ID requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/characters/<character_id> \
        --write-out "\n"
    '''
    character = find_by_id(character_id)
    return jsonify({'character': character}), 200


def save(character):
    '''Persist a character.

    If the character already exists, it will be updated; otherwise, it will be
        created.

    Raises a ValidationError if the character is invalid.
    '''
    character = character.copy()
    validate(character)
    if character.get('id') is None:
        character['id'] = uuid4()
    REPO_CHARACTERS.get('by_id')[character.get('id')] = character
    REPO_CHARACTERS.get('by_account') \
        .setdefault(character.get('account'), []) \
        .append(character)
    return character


def allocate_ability_points(character, **kwargs):
    '''Allocate a character's ability points.

    Raises a ValidationError if the character has insufficient ability points.
    '''
    character = character.copy()
    abilities = character.get('abilities')
    strength = kwargs.get('strength', 0)
    endurance = kwargs.get('endurance', 0)
    agility = kwargs.get('agility', 0)
    accuracy = kwargs.get('accuracy', 0)
    abilities['strength'] += strength
    abilities['endurance'] += endurance
    abilities['agility'] += agility
    abilities['accuracy'] += accuracy
    abilities['unallocated'] -= strength + endurance + agility + accuracy
    if abilities.get('unallocated') < 0:
        raise ValidationError('Insufficient ability points')
    return character


def validate(character):
    '''Validate a character.

    Raises a ValidationError if the provided character is invalid..
    '''
    account = character.get('account')
    name = character.get('name')
    errors = []
    if not account:
        errors.append('Missing required field: account')
    if not name:
        errors.append('Missing required field: name')
    if account and name:
        names = [c.get('name') for c in find_by_account(account)]
        if name in names:
            errors.append('Duplicate character name: %s' % name)
    if errors:
        raise ValidationError(errors=errors)


def find_by_id(character_id):
    '''Find a character with the provided id.

    Raises a NotFoundError if the character could not be found.
    '''
    character = REPO_CHARACTERS.get('by_id').get(character_id)
    if character is None:
        raise NotFoundError('Character not found')
    return character


def find_by_account(account):
    '''Find a characters owned by an account with the provided account ID.'''
    return REPO_CHARACTERS.get('by_account').get(account, [])


def create(**kwargs):
    '''Create a character.

    Characters have the following properties:
        id: a UUID (Universally Unique Identifier)
        account: the ID of the account that owns the character
        name
        level: current level
        experience: current experience points
        health: current health points
        abilities:
            unallocated: unallocated ability points
            strength: increases attack damage
            endurance: increases defense and health
            agility: increases evasion and attack speed
            accuracy: increases normal and critical attack chance
    '''
    abilities = kwargs.get('abilities', {})
    return {
        'id': kwargs.get('id'),
        'account': kwargs.get('account'),
        'name': kwargs.get('name'),
        'level': kwargs.get('level', 1),
        'experience': kwargs.get('experience', 0),
        'health': kwargs.get('health', 1),
        'abilities': {
            'unallocated': abilities.get('unallocated', 0),
            'strength': abilities.get('strength', 0),
            'endurance': abilities.get('endurance', 0),
            'agility': abilities.get('agility', 0),
            'accuracy': abilities.get('accuracy', 0)
        }
    }
