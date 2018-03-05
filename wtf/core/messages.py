'''
wtf.core.messages

Messages have the following properties:
  * id: the message UUID (Universally Unique Identifier)
  * body: the body of the message
  * sender: the account id that send the messages
  * parent: the previous message id (None if no previous message)
  * subject: the subject of the message
  * copies: the recipients copies of the message
  * created_at: the time the message was created
'''
from datetime import datetime
from uuid import uuid4
from wtf.core.errors import NotFoundError, ValidationError

REPO = {'by_id': {}, 'by_parent': {}}

REPO_COPIES = {'by_id': {}, 'by_id_and_recipient': {}, 'by_recipient': {}}


def create(**kwargs):
    '''Create a message.

    Messages have the following properties:
        id: a UUID for the message
        sender: a UUID for the sender
        parent: the UUID for the previous message
        subject: the subject of the message
        body: the body of the message
        recipients: the list of UUID for the recipients
    '''
    message_id = kwargs.get('id')
    body = kwargs.get('body')
    subject = kwargs.get('subject', '(No Subject)')
    recipients = kwargs.get('recipients')
    recipients = recipients if recipients is not None else []
    parent = kwargs.get('parent')
    sender = kwargs.get('sender')
    message = {
        'id': message_id,
        'sender': sender,
        'parent': parent,
        'subject': subject,
        'body': body,
        'copies': [],
        'created_at': datetime.utcnow().isoformat()
    }
    return message


def create_copies(message, recipients):
    '''Creates message copies.
    '''
    copies = []
    print(message)
    print(recipients)
    for recipient in recipients:
        copies.append(create_copy(message, recipient=recipient))
    return copies


def create_copy(message, **kwargs):
    '''Create a message copy

    a Message Copy has the following properties:
        message: a UUID for the original message
        recipient: the UUID of the recipient
        status: the status of the current message: unread, read, deleted, saved
        timestamps: timestamp events for the message copy
    '''
    message_id = message.get('id')
    recipient = kwargs.get('recipient')
    status = kwargs.get('status', 'unread')
    return {
        'message': message_id,
        'recipient': recipient,
        'status': status,
        'timestamps': {
            'read_at': None,
            'deleted_at': None
        }
    }


def save(message):
    '''Persist a message.
    '''
    message = message.copy()
    if message.get('id') is None:
        message['id'] = str(uuid4())
    validate(message)
    for copy in message['copies']:
        copy['message'] = message['id']
        REPO_COPIES.get('by_id').setdefault(copy['message'], []).append(copy)
        REPO_COPIES.get('by_recipient').setdefault(copy['recipient'], []).append(copy)
        REPO_COPIES.get('by_id_and_recipient')[copy['message'] + ',' + copy['recipient']] = copy
    message.pop('copies')
    REPO.get('by_id')[message.get('id')] = message
    if message.get('parent') is not None:
        REPO.get('by_parent').setdefault(message.get('parent'), []).append(message)
    return message


def save_copies(message_copies):
    '''Persist message copies.
    '''
    for message_copy in message_copies:
        save_copy(message_copy)
    return message_copies


def save_copy(message_copy):
    '''Persist a message copy
    '''
    validate_copy(message_copy)
    key = message_copy['message'] + ',' + message_copy['recipient']
    REPO_COPIES.get('by_id').setdefault(message_copy['message'], []).append(message_copy)
    REPO_COPIES.get('by_recipient').setdefault(message_copy['recipient'], []).append(message_copy)
    REPO_COPIES.get('by_id_and_recipient')[key] = message_copy
    return message_copy


def validate(message):
    '''Validate a mesage.

    Raises a ValidationError if the provided message is invalid.
    '''
    subject = message.get('subject')
    body = message.get('body')
    copies = message.get('copies')
    errors = []
    if subject is None:
        errors.append('Missing required field: subject')
    if body is None:
        errors.append('Missing required field: body')
    if copies is None:
        errors.append('Missing required field: copies')
    if errors:
        raise ValidationError(errors=errors)


def validate_copy(message_copy):
    '''Validate a mesage copy.

    Raises a ValidationError if the provided message copy is invalid.
    '''
    recipient = message_copy.get('recipient')
    status = message_copy.get('status')
    timestamps = message_copy.get('timestamps')
    message = message_copy.get('message')
    errors = []
    if recipient is None:
        errors.append('Missing required field: recipient')
    if status is None:
        errors.append('Missing required field: status')
    if timestamps is None:
        errors.append('Missing required field: timestamps')
    if message is None:
        errors.append('Missing required field: message')
    if errors:
        raise ValidationError(errors=errors)


def get_recipient_message_copies(**kwargs):
    '''Retrieves messages for a recipients

    Raises a NotFoundError if recipient could not be found.
    '''
    recipient_id = kwargs.get('recipient')
    status = kwargs.get('status')
    message_copies = find_copies_by_recipient(recipient_id)
    if status:
        message_copies = list(filter(lambda m: m['status'] == str(status), message_copies))
    return message_copies



def find_by_id(message_id):
    '''Find a message with the provided id.

    Raises a NotFoundError if the message could not be found.
    '''
    message = REPO.get('by_id').get(message_id)
    if message is None:
        raise NotFoundError('Message not found')
    return message


def find_by_parent(message_id):
    '''Find messages for a given parent message ID.

    Raises a NotFoundError if the parent message ID could not be found.
    '''
    messages = REPO.get('by_parent').get(message_id)
    if messages is None:
        raise NotFoundError('Parent messages not found')
    return messages



def find_copies_by_recipient(recipient_id):
    '''Find messages that belong to the provided recipient id.

    Raises a NotFoundError if the recipient could not be found.
    '''
    messages = REPO_COPIES.get('by_recipient').get(recipient_id)
    if messages is None:
        raise NotFoundError('Recipient not found')
    return messages


def find_copies_by_id(message_id):
    '''Finds a message copies for a given message ID.

    Raises a NotFoundError if the message copies could not be found.
    '''
    messages = REPO_COPIES.get('by_id').get(message_id)
    if messages is None:
        raise NotFoundError('Message copies not found')
    return messages


def find_copies_by_id_and_recipient(**kwargs):
    '''Finds a message copy for a given message ID and recipient.

    Raises a NotFoundError if the message for the recipient could not be found.
    '''
    message_id = kwargs.get('message_id')
    recipient = kwargs.get('recipient')
    key = message_id + ',' + recipient
    messages = REPO_COPIES.get('by_id_and_recipient').get(key)
    if messages is None:
        raise NotFoundError('Message for Recipient not found')
    return messages


def transform(message, message_copies=None):
    '''Transform a messages

    The following transformations will be performed:
        * copies: added
    '''
    if message_copies is None:
        message_copies = find_copies_by_id(message.get('id'))
    message['copies'] = message_copies
    return message


def transform_copy(message_copy):
    '''Transforms a message copy

    The following transformations will be performed:
        * original: added
    '''
    message_copy['original'] = find_by_id(message_copy['message'])
    return message_copy


def transform_copies(message_copies):
    '''Transform message copies
    '''
    for message_copy in message_copies:
        result = transform_copy(message_copy)
        message_copy.clear()
        message_copy.update(result)
    return message_copies


def transform_all(messages):
    '''Transforms an array of messages
    '''
    for message in messages:
        result = transform(message)
        message.clear()
        message.update(result)
    return messages
