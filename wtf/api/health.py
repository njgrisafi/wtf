'''
wtf.api.health

Health check(s).
'''
from flask import Blueprint


BLUEPRINT = Blueprint('health', __name__)


@BLUEPRINT.route('', methods=['GET'])
def handle_get_request():
    '''Handle healthcheck requests.

    $ curl \
        --request GET \
        --url http://localhost:5000/api/health \
        --write-out "\n"
    '''
    return 'Healthy'
