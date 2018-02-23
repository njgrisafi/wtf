'''
wtf.core.errors

Common exceptions and error handlers used by the core
'''


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
