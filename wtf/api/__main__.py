'''
wtf.api.__main__

The main entrypoint for the API. This module is executed when you run the
    wtf.api module as a script, i.e. `python -m wtf.api`.
'''
import os
from wtf.api.app import create_app


HOST = os.getenv('WTF_API_HOST')
PORT = int(os.getenv('WTF_API_PORT')) if os.getenv('WTF_API_PORT') else None

create_app().run(host=HOST, port=PORT)
