'''
wtf.api.characters

Routes and functions for manipulating characters.
'''
from uuid import uuid4
from flask import Blueprint, request
from wtf import http
from wtf.errors import ValidationError


BLUEPRINT = Blueprint('characters', __name__)
IN_MEMORY_CHARACTERS = {
    'by_id': {},
    'by_account_id': {}
}


@BLUEPRINT.route('', methods=['POST'])
def route_create():
    '''Handle character creation requests.

    $ curl \
        --request POST \
        --url http://localhost:5000/api/characters \
        --header "Content-Type: application/json" \
        --write-out "\n" \
        --data '{
            "accountId": "...",
            "name": "..."
        }'
    '''
    response = None
    try:
        http.validate(content_type='application/json')
        body = request.get_json(silent=True) or {}
        character = save(create(
            account_id=body.get('accountId'),
            name=body.get('name')
        ))
        response = http.success(json=character)
    except ValidationError as error:
        response = http.bad_request(json={'errors': error.errors})
    return response


def save(character):
    '''Persist a character.

    If the character already exists, it will be updated; otherwise, it will be
        created.

    If the character is invalid, a ValidationError will be raised.
    '''
    character = character.copy()
    validate(character)
    if character.get('id') is None:
        character['id'] = uuid4()
    IN_MEMORY_CHARACTERS.get('by_id')[character.get('id')] = character
    IN_MEMORY_CHARACTERS.get('by_account_id') \
        .setdefault(character.get('accountId'), []) \
        .append(character)
    return character


def allocate_ability_points(character, **kwargs):
    '''Allocate a character's ability points.

    If the character has insufficient ability points, a ValidationError will be
        raised.
    '''
    character = character.copy()
    strength = kwargs.get('strength', 0)
    endurance = kwargs.get('endurance', 0)
    agility = kwargs.get('agility', 0)
    accuracy = kwargs.get('accuracy', 0)
    character.get('abilities')['strength'] += strength
    character.get('abilities')['endurance'] += endurance
    character.get('abilities')['agility'] += agility
    character.get('abilities')['accuracy'] += accuracy
    character['ability_points'] -= strength + endurance + agility + accuracy
    if character['ability_points'] < 0:
        raise ValidationError('Insufficient ability points')
    return character


def validate(character):
    '''Validate a character.

    Raises a ValidationError if the provided character is invalid..
    '''
    account_id = character.get('accountId')
    name = character.get('name')
    errors = []
    if not account_id:
        errors.append('Missing required field: accountId')
    if not name:
        errors.append('Missing required field: name')
    if account_id and name:
        names = [c.get('name') for c in find_by_account_id(account_id)]
        if name in names:
            errors.append('Duplicate character name: %s' % name)
    if errors:
        raise ValidationError(errors=errors)


def find_by_account_id(account_id):
    '''Find a characters owned by an account with the given account ID.'''
    return IN_MEMORY_CHARACTERS.get('by_account_id').get(account_id, [])


def create(**kwargs):
    '''Create an character.

    Characters have the following properties:
        id: a UUID (Universally Unique Identifier) for the character
        accountId: the ID of the account that owns the character
        name: the name of the character
        abilities:
            strength: increases attack damage
            endurance: increases defense and health
            agility: increases evasion and attack speed
            accuracy: increases normal and critical attack chance
        ability_points: consumed in order to increase a character's abilities
    '''
    character_id = kwargs.get('id')
    account_id = kwargs.get('account_id')
    name = kwargs.get('name')
    abilities = kwargs.get('abilities', {})
    ability_points = kwargs.get('ability_points', 0)
    return {
        'id': character_id,
        'accountId': account_id,
        'name': name,
        'abilities': {
            'strength': abilities.get('strength', 0),
            'endurance': abilities.get('endurance', 0),
            'agility': abilities.get('agility', 0),
            'accuracy': abilities.get('accuracy', 0)
        },
        'ability_points': ability_points
    }
