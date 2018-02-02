'''
wtf.api.__init__

The War Torn Faith RESTful API is a Flask application that exposes the
    backend logic of the game for clients to consume. While it is mostly
    designed to be consumed by War Torn Faith's web app, third-party consumption
    is also a possibility.
'''
from wtf.api import accounts, characters, health


API_URL_PREFIX = '/api'
API_BLUEPRINTS = {
    '/accounts': accounts.BLUEPRINT,
    '/characters': characters.BLUEPRINT,
    '/health': health.BLUEPRINT
}
