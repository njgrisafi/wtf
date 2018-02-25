# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
from wtf.core import util


def test_salt_and_hash():
    salt_hash = util.salt_and_hash('asdf')
    assert len(salt_hash) == 128
    salt = salt_hash[:64]
    assert util.salt_and_hash('asdf', salt) == salt_hash
    assert util.salt_and_hash_compare('asdf', salt_hash)


def test_interval_intersect():
    expected = 100.0
    actual = util.interval_intersect(
        {'center': 100, 'radius': 25},
        {'center': 100, 'radius': 50}
    )
    assert expected == actual


def test_interval_intersect_no_intersection():
    expected = None
    actual = util.interval_intersect(
        {'center': 100, 'radius': 10},
        {'center': 200, 'radius': 50}
    )
    assert expected == actual


def test_get_interval_grade_value():
    expected = 84.5
    actual = util.interval_grade_value({'center': 100, 'radius': 50}, 0.345)
    assert expected == actual


def test_get_interval_grade_value_negatively_correlated():
    expected = 115.5
    actual = util.interval_grade_value({'center': 100, 'radius': 50}, 1 - 0.345)
    assert expected == actual
