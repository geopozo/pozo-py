from unittest.mock import MagicMock

import lasio
import numpy as np
import pint
import pytest

from pozo import units


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
        result = units.parse_unit_safe(input_value)

        assert isinstance(result, expected_type)
        if expected_str is not None:
            assert str(result) == expected_str
        if is_dimensionless:
            assert result is not None
            assert result.dimensionless


class TestParseUnitFromContext:
    @pytest.mark.parametrize(
        (
            "mnemonic",
            "las_unit",
            "data",
            "expect_none",
            "expect_dimensionless",
            "expected_str",
        ),
        [
            ("DEPTH", "M", [1, 2, 3], False, False, "meter"),
            ("UNKNOWN", "", [1.0, 2.0, 3.0], False, True, "dimensionless"),
            ("UNKNOWN", "invalid_unit_xyz", [1.0, 2.0, 3.0], True, False, None),
            ("DEPTH", "FT", [10, 20], True, False, None),
            ("PRES", "Pa", [1000, 2000], False, False, "pascal"),
        ],
    )
    def test_various_inputs(
        self,
        mnemonic,
        las_unit,
        data,
        expect_none,
        expect_dimensionless,
        expected_str,
    ):
        result = units.parse_unit_from_context(mnemonic, las_unit, data)

        assert isinstance(result, (pint.Unit, type(None)))
        assert (result is None) == expect_none
        assert bool(getattr(result, "dimensionless", False)) == expect_dimensionless
        result_str = (str(result), None)[result is None]
        assert result_str == expected_str


class TestGetUnitFromCurve:
    class MockCurve:
        def __init__(self, mnemonic, unit, data) -> None:
            self.mnemonic = mnemonic
            self.unit = unit
            self.data = data

    @pytest.mark.parametrize(
        ("mnemonic", "unit", "data", "expected"),
        [
            ("DEPTH", "M", [1.0, 2.0, 3.0], "meter"),
            ("ANY", "", [0.1, 0.2], ""),
        ],
    )
    def test_get_unit_from_curve(self, mnemonic, unit, data, expected):
        curve = self.MockCurve(mnemonic, unit, data)
        result = units.get_unit_from_curve(curve)
        if expected == "":
            assert result is not None
            assert result.dimensionless
        else:
            assert isinstance(result, pint.Unit)
            assert str(result) == expected


class TestParseUnitToLas:
    @pytest.mark.parametrize(
        ("mnemonic", "pint_unit", "expected"),
        [
            ("DEPTH", "meter", "M"),
            ("DEPTH", "m", "M"),
            ("DEPTH", units.registry.Unit("meter"), "M"),
            ("DEPTH", units.registry.Unit(""), None),
            ("DEPTH", "", None),
            ("TEMP", units.registry.Unit("degC"), None),
            ("TEMP", "celsius", None),
        ],
    )
    def test_parse_unit_to_las(self, mnemonic, pint_unit, expected):
        result = units.parse_unit_to_las(mnemonic, pint_unit)
        assert result == expected


class TestCheckLas:
    @pytest.fixture
    def mock_las_file(self):
        """Create a mock LAS file with curves for testing."""
        las = MagicMock(spec=lasio.LASFile)
        las.curves = []
        return las

    def add_mock_curve(self, las_file, mnemonic, unit, data, descr=None):
        """Helper to add a mock curve to the LAS file."""
        curve = MagicMock()  # Para similar un objeto Curve de lasio
        curve.mnemonic = mnemonic
        curve.unit = unit
        curve.data = np.array(data)  # Para este caso solo usare numpy arrays
        curve.descr = descr or f"{mnemonic} description"
        las_file.curves.append(curve)
        return curve

    @pytest.mark.parametrize(
        ("curves", "html_output"),
        [
            (
                [
                    ("DEPT", "M", [1, 2, 3], "Depth"),
                    ("GR", "GAPI", [45, 50, 55], "Gamma Ray"),
                ],
                False,
            ),
            (
                [
                    ("DEPT", "M", [1, 2, 3], "Depth"),
                    ("GR", "GAPI", [45, 50, 55], "Gamma Ray"),
                    ("RT", "OHMM", [10, 20, 30], "Resistivity"),
                ],
                True,
            ),
            ([("CALI", "", [8.5, 8.6, 8.7], "Caliper")], False),
        ],
    )
    def test_check_las(self, mock_las_file, curves, html_output):
        expected_keys = [
            "mnemonic",
            "las unit",
            "si unit",
            "pint unit",
            "confidence",
            "comment:",
            "description",
            "min",
            "med",
            "max",
            "#NaN",
        ]
        for mnemonic, unit, data, descr in curves:
            self.add_mock_curve(mock_las_file, mnemonic, unit, data, descr)

        result = units.check_las(mock_las_file, html=html_output)

        if not html_output:
            assert isinstance(result, list)
            assert len(result) == len(curves)

            for i, curve_result in enumerate(result):
                assert isinstance(curve_result, dict)
                assert set(curve_result.keys()) == set(expected_keys)
                assert curve_result["mnemonic"] == curves[i][0]
                assert curve_result["las unit"] == curves[i][1]
                assert curve_result["description"] == curves[i][3]
        else:
            assert result is None
            _ = mock_las_file.curves
