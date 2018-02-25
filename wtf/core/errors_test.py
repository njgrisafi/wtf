# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest
from wtf.core import errors


def test_validation_error():
    expected = 'Validation errors: foobar'
    with pytest.raises(errors.ValidationError) as error:
        raise errors.ValidationError(error='foobar')
    actual = str(error.value)
    assert expected == actual


def test_validation_error_multiple():
    expected = 'Validation errors: foo, bar, baz'
    with pytest.raises(errors.ValidationError) as error:
        raise errors.ValidationError(errors=['foo', 'bar', 'baz'])
    actual = str(error.value)
    assert expected == actual
