'''
wtf.api.messages

Routes and functions for manipulating messages.
'''
from datetime import datetime
from uuid import uuid4
from flask import Blueprint, jsonify, request
from wtf.api import util
from wtf.api.errors import NotFoundError, ValidationError


BLUEPRINT = Blueprint('messages', __name__)
REPO = {'by_id': {}}


@BLUEPRINT.route('', methods=['POST'])
def handle_create_request():
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
    body = util.get_json_body()
    message = save(create(
        subject=body.get('subject'),
        body=body.get('body'),
        recipients=body.get('recipients')
    ))
    return jsonify(message), 200


@BLUEPRINT.route('/<message_id>', methods=['GET'])
def handle_get_by_id_request(message_id):
    '''Handle message retrieval by ID requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/messages/<message_id> \
        --write-out "\n"
    '''
    message = find_by_id(message_id)
    message = message.copy()
    return jsonify({'message': message}), 200


def save(message):
    '''Persist a message.

    Creates a message
    '''
    message = message.copy()
    validate(message)
    if message.get('id') is None:
        message['id'] = str(uuid4())
    REPO.get('by_id')[message.get('id')] = message
    return message


def validate(message):
    '''Validate a mesage.

    Raises a ValidationError if the provided message is invalid..
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


def find_by_id(message_id):
    '''Find an message with the provided id.

    Raises a NotFoundError if the message could not be found.
    '''
    message = REPO.get('by_id').get(message_id)
    if message is None:
        raise NotFoundError('Message not found')
    return message


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
    try:
        message_id = kwargs.get('id')
        body = kwargs.get('body')
        subject = kwargs.get('subject', '(No Subject)')
        recipients = kwargs.get('recipients')
        if not recipients:
            recipients = []
        message = {
            'id': message_id,
            'sender': None,
            'parent': None,
            'subject': subject,
            'body': body,
            'copies': [],
            'created_at': datetime.utcnow().isoformat()
        }
        for r in recipients:
            message['copies'].append(create_copy(message, recipient=r))
        return message
    except Exception as e:
        print(e)


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
