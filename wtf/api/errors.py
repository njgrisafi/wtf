'''
wtf.api.errors

Common exceptions and error handlers used by the API
'''
from flask import jsonify


def handle_invalid_request(error):
    '''Handle ValidationError errors.'''
    return jsonify({'errors': error.errors}), 400


def handle_not_found(error):
    '''Handle NotFoundError errors.'''
    return jsonify({'errors': [str(error)]}), 404


# pylint: disable=unused-argument
def handle_error(error):
    '''Handle errors not caught by another error handler.'''
    return jsonify({'errors': ['Internal Server Error']}), 500


class ValidationError(Exception):
    '''Represents one-to-many validation errors.'''

    errors = []

    def __init__(self, error=None, errors=None):
        super(ValidationError, self).__init__()
        self.errors = [error] if error else errors if errors else []

    def __str__(self):
        errors_str = ', '.join(self.errors) if self.errors else '(none)'
        return 'Validation errors: %s' % errors_str


class NotFoundError(Exception):
    '''Represents a resource not found error.'''

    pass
