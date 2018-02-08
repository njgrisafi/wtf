'''
wtf.web.__main__

The main entrypoint for the web app. This module is executed when you run the
    wtf.web module as a script, i.e. `python -m wtf.web`.
'''
import os
from wtf.web.app import create_app

HOST = os.getenv('WTF_WEB_HOST')
PORT = int(os.getenv('WTF_WEB_PORT')) if os.getenv('WTF_WEB_PORT') else None

create_app().run(host=HOST, port=PORT)
