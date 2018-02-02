'''
wtf.api.__main__

The main entrypoint for the API. This module is executed when you run the
    wtf.api module as a script, i.e. `python -m wtf.api`.
'''
from wtf.api.app import create_app


if __name__ == '__main__':
    create_app().run()
