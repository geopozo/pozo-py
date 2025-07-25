import pint
import pytest

from pozo.units import parse_unit_safe


class TestParseUnitSafe:
    @pytest.mark.parametrize(
        ("input_value", "expected_type", "expected_str", "is_dimensionless"),
        [
            ("meter", pint.Unit, "meter", False),
            ("m", pint.Unit, "meter", False),
            ("", pint.Unit, "dimensionless", True),
            ("invalid_unit_xyz", type(None), None, False),
        ],
    )
    def test_parse_unit_safe_cases(
        self,
        input_value,
        expected_type,
        expected_str,
        is_dimensionless,
    ):
        result = parse_unit_safe(input_value)

        assert isinstance(result, expected_type)
        if expected_str is not None:
            assert str(result) == expected_str
        if is_dimensionless:
            assert result is not None
            assert result.dimensionless
