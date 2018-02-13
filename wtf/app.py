'''
wtf.app

The War Torn Faith bundled app.
'''
from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware
from wtf.api import API_PREFIX
from wtf.api.app import create_app as create_api_app
from wtf.web.app import create_app as create_web_app


def create_app():
    '''Create the bundled Werkzeug application'''
    app = Flask(__name__)
    app.wsgi_app = DispatcherMiddleware(
        create_web_app(),
        {API_PREFIX: create_api_app(prefix='')}
    )
    return app
