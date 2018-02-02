'''
wtf.web.app

The War Torn Faith web app.
'''
from flask import Flask


def create_app():
    '''Create the web app Flask application'''
    app = Flask(__name__)
    app.route('/hello')(lambda: 'Hello, world!')
    return app
