'''
wtf.api.app

The War Torn Faith API app.
'''
from flask import Flask
from wtf.api import routes, API_PREFIX


def create_app(prefix=API_PREFIX):
    '''Create the API Flask application'''
    app = Flask(__name__)
    app.register_blueprint(routes.BLUEPRINT, url_prefix='%s' % prefix)
    return app
