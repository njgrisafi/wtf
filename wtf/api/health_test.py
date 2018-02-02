# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
from wtf.api import health


def test_route_healthcheck():
    assert health.route_healthcheck() == 'Healthy'
