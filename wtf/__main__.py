'''
wtf.__main__

The main entrypoint for the bundled app. This module is executed when you run
    the wtf module as a script, i.e. `python -m wtf`.
'''
import os
from wtf.app import create_app

HOST = os.getenv('WTF_HOST')
PORT = int(os.getenv('WTF_PORT')) if os.getenv('WTF_PORT') else None

create_app().run(host=HOST, port=PORT)
