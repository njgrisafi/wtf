# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from mock import patch
from wtf.api import errors


@patch('wtf.api.errors.jsonify')
def test_handle_invalid_request_error(mock_jsonify):
    mock_jsonify.return_value = 'foobar'
    error = errors.ValidationError(errors=['foo', 'bar', 'baz'])
    response, status_code = errors.handle_invalid_request(error)
    assert response == 'foobar'
    assert status_code == 400
    mock_jsonify.assert_called_with({'errors': ['foo', 'bar', 'baz']})


@patch('wtf.api.errors.jsonify')
def test_handle_not_found_error(mock_jsonify):
    mock_jsonify.return_value = 'foobar'
    error = errors.NotFoundError('Foobar not found')
    response, status_code = errors.handle_not_found(error)
    assert response == 'foobar'
    assert status_code == 404
    mock_jsonify.assert_called_with({'errors': ['Foobar not found']})


@patch('wtf.api.errors.jsonify')
def test_handle_misc_error(mock_jsonify):
    mock_jsonify.return_value = 'foobar'
    error = Exception('foo bar baz')
    response, status_code = errors.handle_error(error)
    assert response == 'foobar'
    assert status_code == 500
    mock_jsonify.assert_called_with({'errors': ['Internal Server Error']})


def test_validation_exception_to_string():
    expected = 'Validation errors: foo, bar, baz'
    with pytest.raises(errors.ValidationError) as error:
        raise errors.ValidationError(errors=['foo', 'bar', 'baz'])
    actual = str(error.value)
    assert expected == actual
