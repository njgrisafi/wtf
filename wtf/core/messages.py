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

REPO = {'by_id': {}, 'by_recipient': {}}


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
    for recipient in recipients:
        message['copies'].append(create_copy(message, recipient=recipient))
    return message

def save(message):
    '''Persist a message.

    Creates a message
    '''
    print("crazy")
    message = message.copy()
    if message.get('id') is None:
        message['id'] = str(uuid4())
    validate(message)
    for copy in message['copies']:
        copy['message'] = message['id']
        REPO.get('by_recipient').setdefault(copy['recipient'], []).append(copy)
    REPO.get('by_id')[message.get('id')] = message
    return message


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


def get_recipient_messages(**kwargs):
    '''Retrieves messages for a recipients

    Raises a NotFoundError if recipient could not be found.
    '''
    recipient_id = kwargs.get('recipient')
    status = kwargs.get('status')
    message_copies = find_by_recipient(recipient_id)
    if status:
        message_copies = list(filter(lambda m: m['status'] == str(status), message_copies))
    return list(map(lambda m: find_by_id(m['message']), message_copies))



def find_by_id(message_id):
    '''Find an message with the provided id.

    Raises a NotFoundError if the message could not be found.
    '''
    message = REPO.get('by_id').get(message_id)
    if message is None:
        raise NotFoundError('Message not found')
    return message


def find_by_recipient(recipient_id):
    '''Find messages that belong to the provided recipient id.

    Raises a NotFoundError if the recipient could not be found.
    '''
    messages = REPO.get('by_recipient').get(recipient_id)
    if messages is None:
        raise NotFoundError('Recipient not found')
    return messages


def create_copy(message, **kwargs):
    '''Create a message copy

    MessageCopies have the following properties:
        message: a UUID for the original message
        recipient: the UUID of the recipient
        status: the status of the current message: unread, read, deleted, saved
        read_at: the time the recipient read the mesaage
        deleted_at: the time the recipient deleted the message
    '''
    message_id = message.get('id')
    recipient = kwargs.get('recipient')
    status = kwargs.get('status', 'unread')
    return {
        'message': message_id,
        'recipient': recipient,
        'status': status,
        'read_at': None,
        'deleted_at': None
    }
