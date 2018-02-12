'''
wtf.api.accounts

Routes and functions for manipulating accounts.
'''
from uuid import uuid4
from flask import Blueprint, jsonify, request
from wtf.api import util
from wtf.api.errors import NotFoundError, ValidationError


BLUEPRINT = Blueprint('accounts', __name__)
REPO = {'by_id': {}, 'by_email': {}}


@BLUEPRINT.route('', methods=['POST'])
def handle_create_request():
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
    util.validate_request(content_type='application/json')
    body = request.get_json(silent=True) or {}
    account = save(create(
        email=body.get('email'),
        password=body.get('password')
    ))
    return jsonify(account), 200


@BLUEPRINT.route('/<account_id>', methods=['GET'])
def handle_get_by_id_request(account_id):
    '''Handle account retrieval by ID requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/accounts/<account_id> \
        --write-out "\n"
    '''
    account = find_by_id(account_id)
    account = account.copy()
    account.pop('password')
    return jsonify({'account': account}), 200


def save(account):
    '''Persist an account.

    If the account already exists, it will be updated; otherwise, it will be
        created.
    '''
    account = account.copy()
    validate(account)
    if account.get('id') is None:
        account['id'] = str(uuid4())
    REPO.get('by_id')[account.get('id')] = account
    REPO.get('by_email')[account.get('email')] = account
    return account


def validate(account):
    '''Validate an account.

    Raises a ValidationError if the provided account is invalid..
    '''
    email = account.get('email')
    password = account.get('password')
    errors = []
    if not email:
        errors.append('Missing required field: email')
    elif find_by_email(email) is not None:
        errors.append('Email address already registered')
    if not password:
        errors.append('Missing required field: password')
    if errors:
        raise ValidationError(errors=errors)


def find_by_email_password(email, password):
    '''Find an account with the provided email address and password.

    This function is intended to be used with account
        authentication - it will return `None` if the supplied email and
        password combination is incorrect. Note that the password supplied to
        this function is the account's plaintext password.

    Raises a NotFoundError if the account could not be found.
    '''
    account = find_by_email(email)
    if not util.salt_and_hash_compare(password, account.get('password')):
        raise NotFoundError('Account not found')
    return account


def find_by_id(account_id):
    '''Find an account with the provided id.

    Raises a NotFoundError if the account could not be found.
    '''
    account = REPO.get('by_id').get(account_id)
    if account is None:
        raise NotFoundError('Account not found')
    return account


def find_by_email(email):
    '''Find an account with the provided email address.

    Raises a NotFoundError if the account could not be found.
    '''
    account = REPO.get('by_email').get(email)
    if account is None:
        raise NotFoundError('Account not found')
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
