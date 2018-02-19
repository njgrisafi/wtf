# pylint: disable=missing-docstring,invalid-name
import pytest
from mock import Mock, patch
from werkzeug.exceptions import BadRequest
from wtf.api import util
from wtf.api.errors import ValidationError


def test_salt_and_hash():
    salt_hash = util.salt_and_hash('asdf')
    assert len(salt_hash) == 128
    salt = salt_hash[:64]
    assert util.salt_and_hash('asdf', salt) == salt_hash
    assert util.salt_and_hash_compare('asdf', salt_hash)


@patch('wtf.api.util.request')
def test_get_json_body_content_type_not_json(mock_request):
    expected = 'Content-Type header must be: application/json'
    mock_request.content_type = 'application/html'
    with pytest.raises(ValidationError) as e:
        util.get_json_body()
    actual = e.value.errors
    assert expected in actual


@patch('wtf.api.util.request')
def test_get_json_body_invalid(mock_request):
    expected = 'Unable to parse JSON request body'
    mock_request.content_type = 'application/json'
    mock_request.get_json = Mock(side_effect=BadRequest())
    with pytest.raises(ValidationError) as e:
        util.get_json_body()
    actual = e.value.errors
    assert expected in actual
