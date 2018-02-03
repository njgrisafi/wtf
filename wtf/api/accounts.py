'''
wtf.api.accounts

Routes and functions for manipulating accounts.
'''
from uuid import uuid4
from flask import Blueprint, request
from wtf import http
from wtf.api import util


BLUEPRINT = Blueprint('accounts', __name__)
IN_MEMORY_ACCOUNTS = {
    'by_id': {},
    'by_email': {}
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
    body = request.get_json(silent=True) or {}
    errors = []
    if request.content_type != 'application/json':
        errors.append('Content-Type header must be: application/json')
    else:
        if 'email' not in body:
            errors.append('Missing required field: email')
        elif find_by_email(body.get('email')) is not None:
            errors.append('Email address already registered')
        if 'password' not in body:
            errors.append('Missing required field: password')
    response = None
    if errors:
        response = http.bad_request(json={'errors': errors})
    else:
        account = save(create(
            email=body.get('email'),
            password=body.get('password')
        ))
        response = http.success(json=account)
    return response


def find_by_id(account_id):
    '''Find an account with the given id.'''
    return IN_MEMORY_ACCOUNTS.get('by_id').get(account_id)


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


def save(account):
    '''Persist an account.

    If the account already exists, it will be updated; otherwise, it will be
        created.
    '''
    if account.get('id') is None:
        account['id'] = uuid4()
    IN_MEMORY_ACCOUNTS.get('by_id')[account.get('id')] = account
    IN_MEMORY_ACCOUNTS.get('by_email')[account.get('email')] = account
    return account


def create(**kwargs):
    '''Create an account.

    Accounts have the following properties:
        id: a UUID (Universally Unique Identifier) for the account
        email: an email address that the player can be reached at
        password: the password used to authenticate as the account
    '''
    account_id = kwargs.get('id')
    email = kwargs.get('email')
    password = kwargs.get('password')
    return {
        'id': account_id,
        'email': email,
        'password': util.salt_and_hash(password) if password else None
    }
