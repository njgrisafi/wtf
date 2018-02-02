'''
wtf.__main__

The main entrypoint for the bundled app. This module is executed when you run
    the wtf module as a script, i.e. `python -m wtf`.
'''


if __name__ == '__main__':
    from wtf.app import create_app
    create_app().run()
