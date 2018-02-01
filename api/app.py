from flask import Flask
from api import BLUEPRINTS


app = Flask(__name__)
for path in BLUEPRINTS.keys():
    app.register_blueprint(BLUEPRINTS.get(path), url_prefix='/api%s' % path)
