'''The War Torn Faith RESTful API is a Flask application that exposes the
backend logic of the game for clients to consume. While it is mostly designed to
be consumed by War Torn Faith's web app, third-party consumption is also a
possibility.
'''
from . import accounts, characters, health


BLUEPRINTS = {
    '/accounts': accounts.BLUEPRINT,
    '/characters': characters.BLUEPRINT,
    '/health': health.BLUEPRINT
}
