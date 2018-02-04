# pylint: disable=missing-docstring,invalid-name,redefined-outer-name
import pytest
from wtf.errors import ValidationError


def test_validation_exception_as_string():
    expected = 'Validation errors: foo, bar, baz'
    with pytest.raises(ValidationError) as error:
        raise ValidationError(errors=['foo', 'bar', 'baz'])
    actual = str(error.value)
    assert expected == actual
