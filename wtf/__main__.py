'''
wtf.__main__

The main entrypoint for the bundled app. This module is executed when you run
    the wtf module as a script, i.e. `python -m wtf`.
'''
from wtf.app import create_app


create_app().run()
