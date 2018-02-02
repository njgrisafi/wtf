# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
from flask import Flask
from wtf.web.app import create_app


def test_create_app():
    app = create_app()
    assert isinstance(app, Flask)
