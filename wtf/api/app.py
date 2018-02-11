'''
wtf.api.app

The War Torn Faith API app.
'''
from flask import Flask
from wtf.api import API_BLUEPRINTS, API_ERROR_HANDLERS, API_URL_PREFIX


def create_app(prefix=API_URL_PREFIX):
    '''Create the API Flask application'''
    app = Flask(__name__)
    for path, blueprint in API_BLUEPRINTS:
        app.register_blueprint(blueprint, url_prefix='%s%s' % (prefix, path))
    for error, handler in API_ERROR_HANDLERS:
        app.register_error_handler(error, handler)
    return app
