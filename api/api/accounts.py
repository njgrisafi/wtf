'''Routes and functions for manipulating accounts'''
from uuid import uuid4
from flask import Blueprint, jsonify, make_response, request
from . import util


BLUEPRINT = Blueprint('accounts', __name__)
IN_MEMORY_ACCOUNTS = {
    'by_uuid': {},
    'by_email': {},
    'by_username': {}
}


@BLUEPRINT.route('', methods=['POST'])
def route_create_account():
    '''Handle account creation requests.

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
    errors = []
    if request.content_type != 'application/json':
        errors.append('Content-Type header must be: application/json')
    else:
        body = request.get_json(silent=True) or {}
        if 'email' not in body:
            errors.append('Missing required field: email')
        elif find_by_email(body.get('email')) is not None:
            errors.append(
                'An account is already registered with the provided email '
                + 'address.'
            )
        if 'password' not in body:
            errors.append('Missing required field: password')
    response_body = None
    response_code = 200
    if errors:
        response_body = {'errors': errors}
        response_code = 400
    else:
        response_body = save(create(
            email=body.get('email'),
            password=body.get('password')
        ))
    return make_response(jsonify(response_body), response_code)


def create(uuid=None, email=None, password=None):
    '''Create an account.

    Accounts have the following properties:
        uuid: a "universally unique identifier" for the account
        email: an email address that the player can be reached at
        password: the password used to authenticate as the account
    '''
    return {
        'uuid': uuid,
        'email': email,
        'password': util.salt_and_hash(password) if password else None
    }


def save(account):
    '''Persist an account.

    If the account already exists, it will be updated; otherwise, it will be
        created.
    '''
    if account.get('uuid') is None:
        account['uuid'] = uuid4()
    IN_MEMORY_ACCOUNTS.get('by_uuid')[account.get('uuid')] = account
    IN_MEMORY_ACCOUNTS.get('by_email')[account.get('email')] = account
    return account


def find_by_uuid(uuid):
    '''Find an account with the given UUID.'''
    return IN_MEMORY_ACCOUNTS.get('by_uuid').get(uuid)


def find_by_email(email):
    '''Find an account with the given email address.'''
    return IN_MEMORY_ACCOUNTS.get('by_email').get(email)


def find_by_email_password(email, password):
    '''Find an account with the given email address and password.

    This function is intended to be used with account
    authentication - it will return `None` if the supplied email and
    password combination is incorrect. Note that the password supplied to this
    function is the account's plaintext password.
    '''
    account = find_by_email(email)
    if account is not None:
        if not util.salt_and_hash_compare(password, account.get('password')):
            account = None
    return account
