'''
wtf.core.accounts

Accounts have the following properties:
  * id: the account's UUID (Universally Unique Identifier)
  * email: an email address that the player can be reached at
  * password: the password used to authenticate as the account
'''
from uuid import uuid4
from wtf.core import util
from wtf.core.errors import NotFoundError, ValidationError


REPO = {'by_id': {}, 'by_email': {}}


def create(**kwargs):
    '''Create an account.'''
    password = kwargs.get('password')
    return {
        'id': kwargs.get('id'),
        'email': kwargs.get('email'),
        'password': util.salt_and_hash(password) if password else None
    }


def save(account):
    '''Create/update an account.'''
    account = account.copy()
    if account.get('id') is None:
        account['id'] = str(uuid4())
    validate(account)
    REPO.get('by_id')[account.get('id')] = account
    REPO.get('by_email')[account.get('email')] = account
    return account


def validate(account):
    '''Validate an account.

    Raises a ValidationError if the account is invalid.
    '''
    account_id = account.get('id')
    email = account.get('email')
    password = account.get('password')
    errors = []
    if not account_id:
        errors.append('Missing required field: id')
    if not email:
        errors.append('Missing required field: email')
    else:
        try:
            find_by_email(email)
            errors.append('Email address already registered')
        except NotFoundError:
            pass
    if not password:
        errors.append('Missing required field: password')
    if errors:
        raise ValidationError(errors=errors)


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


def find_by_email_password(email, password):
    '''Find an account with the provided email address and plaintext password.

    Raises a NotFoundError if the account could not be found.
    '''
    account = find_by_email(email)
    if not util.salt_and_hash_compare(password, account.get('password')):
        raise NotFoundError('Account not found')
    return account


def transform(account):
    '''Transform an account.

    The following transformations will be performed:
      * password: removed
    '''
    account = account.copy()
    account.pop('password')
    return account
