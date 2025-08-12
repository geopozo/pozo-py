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
            ("DEPTH", "m", [5, 6, 7], "meter"),
            ("PRES", "Pa", [1000, 2000], "pascal"),
            ("TEMP", "K", [273.15, 300.0], "kelvin"),
            ("PORO", "", [0.25, 0.3, 0.35], ""),
            ("UNKNOWN", "", [1.0, 2.0], ""),
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
        ("curves", "expected"),
        [
            (
                [
                    ("CALI", "", [8.5, 8.6, 8.7], "Caliper"),
                    ("GR", "GAPI", [45, 50, 55], "Gamma Ray"),
                ],
                {
                    "mnemonic": ["CALI", "GR"],
                    "las unit": ["", "GAPI"],
                    "si unit": ["", "gAPI"],
                    "pint unit": [pint.Unit(""), pint.Unit("gamma_API_unit")],
                    "confidence": [0, 100],
                    "comment": [" for CALI", "Clear match."],
                    "description": ["Caliper", "Gamma Ray"],
                    "min": ["8.5", "45.0"],
                    "med": ["8.6", "50.0"],
                    "max": ["8.7", "55.0"],
                    "#NaN": [0, 0],
                },
            ),
            (
                [
                    ("GR", "GAPI", [45, 50, 55], "Gamma Ray"),
                    ("RT", "OHMM", [10, 20, 30], "Resistivity"),
                ],
                {
                    "mnemonic": ["GR", "RT"],
                    "las unit": ["GAPI", "OHMM"],
                    "si unit": ["gAPI", ""],
                    "pint unit": [pint.Unit("gamma_API_unit"), pint.Unit("")],
                    "confidence": [100, 0],
                    "comment": ["Clear match.", "OHMM for RT"],
                    "description": ["Gamma Ray", "Resistivity"],
                    "min": ["45.0", "10.0"],
                    "med": ["50.0", "20.0"],
                    "max": ["55.0", "30.0"],
                    "#NaN": [0, 0],
                },
            ),
        ],
    )
    def test_check_las(self, mock_las_file, curves, expected):
        expected_keys = [
            "mnemonic",
            "las unit",
            "si unit",
            "pint unit",
            "confidence",
            "comment",
            "description",
            "min",
            "med",
            "max",
            "#NaN",
        ]
        for mnemonic, unit, data, descr in curves:
            self.add_mock_curve(mock_las_file, mnemonic, unit, data, descr)

        result = units.check_las(mock_las_file, html=False)

        assert result == expected
        assert isinstance(result, dict)
        assert list(result.keys()) == expected_keys
