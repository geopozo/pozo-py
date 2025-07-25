import pint
import pytest

from pozo.units import parse_unit_from_context, parse_unit_safe


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


class TestParseUnitFromContext:
    @pytest.mark.parametrize(
        ("mnemonic", "las_unit", "data", "expected"),
        [
            ("DEPTH", "M", [1, 2, 3], "meter"),
            ("UNKNOWN", "", [1.0, 2.0, 3.0], ""),  # dimensionless
            ("UNKNOWN", "invalid_unit_xyz", [1.0, 2.0, 3.0], None),
        ],
    )
    def test_various_inputs(self, mnemonic, las_unit, data, expected):
        result = parse_unit_from_context(mnemonic, las_unit, data)
        if expected is None:
            assert result is None
        elif expected == "":
            assert result is not None
            assert result.dimensionless
        else:
            assert isinstance(result, pint.Unit)
            assert str(result) == expected
