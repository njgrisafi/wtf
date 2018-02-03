'''
wtf.api.characters

Routes and functions for manipulating characters.
'''
from uuid import uuid4
from flask import Blueprint, request
from wtf import http


BLUEPRINT = Blueprint('characters', __name__)
IN_MEMORY_CHARACTERS = {
    'by_id': {},
    'by_account_id': {}
}


@BLUEPRINT.route('', methods=['POST'])
def route_create_character():
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
    body = request.get_json(silent=True) or {}
    errors = []
    if request.content_type != 'application/json':
        errors.append('Content-Type header must be: application/json')
    else:
        if 'accountId' not in body:
            errors.append('Missing required field: accountId')
        if 'name' not in body:
            errors.append('Missing required field: name')
        if set(('accountId', 'name')).issubset(body):
            characters = find_by_account_id(body.get('accountId')) or []
            if body.get('name') in [c.get('name') for c in characters]:
                errors.append('Duplicate character name: %s' % body.get('name'))
    response = None
    if errors:
        response = http.bad_request(json={'errors': errors})
    else:
        character = save(create(
            account_id=body.get('accountId'),
            name=body.get('name')
        ))
        response = http.success(json=character)
    return response


def find_by_account_id(account_id):
    '''Find a characters owned by an account with the given account ID.'''
    return IN_MEMORY_CHARACTERS.get('by_account_id').get(account_id)


def save(character):
    '''Persist a character.

    If the character already exists, it will be updated; otherwise, it will be
        created.
    '''
    if character.get('id') is None:
        character['id'] = uuid4()
    IN_MEMORY_CHARACTERS.get('by_id')[character.get('id')] = character
    IN_MEMORY_CHARACTERS.get('by_account_id') \
        .setdefault(character.get('accountId'), []) \
        .append(character)
    return character


def create(**kwargs):
    '''Create an character.

    Characters have the following properties:
        id: a UUID (Universally Unique Identifier) for the character
        accountId: the ID of the account that owns the character
        name: the name of the character
    '''
    character_id = kwargs.get('id')
    account_id = kwargs.get('account_id')
    name = kwargs.get('name')
    return {'id': character_id, 'accountId': account_id, 'name': name}
