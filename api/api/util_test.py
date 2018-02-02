# pylint: disable=missing-docstring,invalid-name
from . import util


def test_salt_and_hash():
    salt_hash = util.salt_and_hash('asdf')
    assert len(salt_hash) == 128
    salt = salt_hash[:64]
    assert util.salt_and_hash('asdf', salt) == salt_hash
    assert util.salt_and_hash_compare('asdf', salt_hash)
