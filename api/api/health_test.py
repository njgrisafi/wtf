# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
from . import health


def test_route_healthcheck():
    assert health.route_healthcheck() == 'Healthy'
