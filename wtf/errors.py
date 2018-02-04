'''
wtf.errors

Common exceptions used throughout the project.
'''


class ValidationError(Exception):
    '''Represents one-to-many validation errors.'''

    errors = []

    def __init__(self, errors=None):
        super(ValidationError, self).__init__()
        self.errors = errors or []

    def __str__(self):
        errors_str = ', '.join(self.errors) if self.errors else '(none)'
        return 'Validation errors: %s' % errors_str
