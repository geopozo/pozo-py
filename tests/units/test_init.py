import pint
import pytest

from pozo.units import (
    get_unit_from_curve,
    parse_unit_from_context,
    parse_unit_safe,
    parse_unit_to_las,
    registry,
)


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
            ("UNKNOWN", "", [1.0, 2.0, 3.0], ""),
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


class TestGetUnitFromCurve:
    class MockCurve:
        def __init__(self, mnemonic, unit, data) -> None:
            self.mnemonic = mnemonic
            self.unit = unit
            self.data = data

    @pytest.mark.parametrize(
        ("mnemonic", "unit", "data", "expected"),
        [("DEPTH", "M", [1.0, 2.0, 3.0], "meter"), ("ANY", "", [0.1, 0.2], "")],
    )
    def test_get_unit_from_curve(self, mnemonic, unit, data, expected):
        curve = self.MockCurve(mnemonic, unit, data)
        result = get_unit_from_curve(curve)
        if expected == "":
            assert result is not None
            assert result.dimensionless
        else:
            assert isinstance(result, pint.Unit)
            assert str(result) == expected


class TestParseUnitToLas:
    @pytest.mark.parametrize(
        ("curve", "unit_input", "expected"),
        [
            ("DEPTH", "meter", "M"),
            ("DEPTH", "m", "M"),
            ("DEPTH", registry.Unit("meter"), "M"),
            ("DEPTH", registry.Unit(""), None),
            ("DEPTH", "", None),
            ("TEMP", registry.Unit("degC"), None),
            ("TEMP", "celsius", None),
        ],
    )
    def test_parse_unit_to_las(self, curve, unit_input, expected):
        result = parse_unit_to_las(curve, unit_input)
        assert result == expected
