'''
wtf.web.__main__

The main entrypoint for the web app. This module is executed when you run the
    wtf.web module as a script, i.e. `python -m wtf.web`.
'''


if __name__ == '__main__':
    from wtf.web.app import create_app
    create_app().run()
