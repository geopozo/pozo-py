"""Tests for pozo.units.__init__ module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pint
import pytest

from pozo.units import (
    check_las,
    get_unit_from_curve,
    parse_unit_from_context,
    parse_unit_safe,
    parse_unit_to_las,
    registry,
)


class TestCheckLas:
    """Test the check_las function."""

    def _create_mock_curve(
        self,
        mnemonic: str,
        unit: str,
        data: list,
        descr: str = "Test description",
    ) -> Mock:
        """Create a mock curve object for testing."""
        curve = Mock()
        curve.mnemonic = mnemonic
        curve.unit = unit
        curve.data = data
        curve.descr = descr
        return curve

    def _create_mock_las_file(self, curves: list[Mock]) -> Mock:
        """Create a mock LAS file object for testing."""
        las_file = Mock()
        las_file.curves = curves
        return las_file

    def test_check_las_valid_args_html_true_returns_none(self) -> None:
        """Test check_las with valid args and html=True returns None."""
        curve1 = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        curve2 = self._create_mock_curve("GR", "API", [10.0, 20.0, 30.0])

        las_file = self._create_mock_las_file([curve1, curve2])

        mock_diagnosis = {
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }
        # los parches estan para evitar probar las funciones
        # pero tambien fijan las funciones y sus nombres como necesario
        # y realmente no es necesario todo esto
        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                return_value=registry.parse_units("meter"),
            ),
            patch("pozo.units.display.show_content"),
        ):
            result = check_las(las_file, html=True)

            assert result is None

    def test_check_las_valid_args_html_false_returns_list(self) -> None:
        """Test check_las with valid args and html=False returns a valid list."""
        curve1 = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        curve2 = self._create_mock_curve("GR", "API", [10.0, 20.0, 30.0])

        las_file = self._create_mock_las_file([curve1, curve2])

        mock_diagnosis = {  # mucha duplicación de codigo
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }

        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                return_value=registry.parse_units("meter"),
            ),
        ):
            result = check_las(las_file, html=False)

            two_curves = 2
            assert result is not None
            assert isinstance(result, list)
            assert len(result) == two_curves

            exp_confidence = 95
            assert isinstance(result[0], dict)
            assert result[0]["mnemonic"] == "DEPTH"
            assert result[0]["las unit"] == "M"
            assert result[0]["si unit"] == "meter"
            assert result[0]["confidence"] == exp_confidence
            assert result[0]["comment:"] == "High confidence"

    def test_check_las_html_generation(self) -> None:
        """Test HTML generation functionality."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])

        mock_diagnosis = {
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }

        div_id = "test-div"

        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                return_value=registry.parse_units("meter"),
            ),
            patch(
                "pozo.units._table.generate_html_table",
                return_value="<table>test</table>",
            ) as mock_html_table,
            patch("pozo.units.display.show_content") as mock_show_content,
        ):
            result = check_las(las_file, html=True, div_id=div_id)

            assert result is None
            mock_html_table.assert_called_once()  # por que
            mock_show_content.assert_called_once()

            call_args = mock_show_content.call_args
            assert f'<div id="{div_id}"><table>test</table></div>' in call_args[0][0]

    def test_check_las_error_in_las_to_si_diagnosis(self) -> None:
        """Test error handling when las_to_si_diagnosis raises an exception."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])
        # vamos a forzar un error, y revisar el error. por. que.
        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                side_effect=Exception("Diagnosis error"),
            ),
            pytest.raises(Exception, match="Diagnosis error"),
        ):
            check_las(las_file, html=False)

    def test_check_las_error_in_parse_unit_from_context(self) -> None:
        """Test error handling when parse_unit_from_context raises an exception."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])

        mock_diagnosis = {
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }

        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                side_effect=Exception("Parse error"),
            ),
            pytest.raises(Exception, match="Parse error"),
        ):
            check_las(las_file, html=False)
            # otras vez estamos revisando que funcione un patch en vez del
            # comportamiento de la function?

    def test_check_las_error_in_html_table_generation(self) -> None:
        """Test error handling when HTML table generation raises an exception."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])

        mock_diagnosis = {
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }

        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                return_value=registry.parse_units("meter"),
            ),
            patch(
                "pozo.units._table.generate_html_table",
                side_effect=Exception("HTML table error"),
            ),
            pytest.raises(Exception, match="HTML table error"),
        ):
            check_las(las_file, html=True)

    def test_check_las_error_in_display_show_content(self) -> None:
        """Test error handling when display.show_content raises an exception."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])

        mock_diagnosis = {
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }

        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                return_value=registry.parse_units("meter"),
            ),
            patch(
                "pozo.units._table.generate_html_table",
                return_value="<table>test</table>",
            ),
            patch(
                "pozo.units.display.show_content",
                side_effect=Exception("Display error"),
            ),
            pytest.raises(Exception, match="Display error"),
        ):
            check_las(las_file, html=True)

    def test_check_las_empty_curves_list(self) -> None:
        """Test check_las with empty curves list."""
        las_file = self._create_mock_las_file([])

        result = check_las(las_file, html=False)  # bueno
        assert result == []

    def test_check_las_none_values_in_diagnosis(self) -> None:
        """Test check_las handles None values in diagnosis properly."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])

        mock_diagnosis = {
            "si_unit": None,
            "confidence": None,
            "comment": None,
            "v_min": None,
            "v_med": None,
            "v_max": None,
            "n_nan": None,
        }
        # por que estamos rehaciendo un mock y patch cada vez. mejor armar un
        # ejemplo fijo y correcto con todas las instancias y probar eso.
        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch("pozo.units.parse_unit_from_context", return_value=None),
        ):
            result = check_las(las_file, html=False)

            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 1

            curve_data = result[0]
            if isinstance(curve_data, dict):
                assert curve_data["si unit"] is None
                assert curve_data["pint unit"] is None
                assert curve_data["confidence"] is None

    def test_check_las_with_custom_div_id(self) -> None:
        """Test check_las with custom div_id parameter."""
        curve = self._create_mock_curve("DEPTH", "M", [1.0, 2.0, 3.0])
        las_file = self._create_mock_las_file([curve])

        mock_diagnosis = {
            "si_unit": "meter",
            "confidence": 95,
            "comment": "High confidence",
            "v_min": "1.0",
            "v_med": "2.0",
            "v_max": "3.0",
            "n_nan": 0,
        }

        custom_div_id = "custom-test-div"

        with (
            patch(
                "pozo.units.las_map.las_to_si_diagnosis",
                return_value=mock_diagnosis,
            ),
            patch(
                "pozo.units.parse_unit_from_context",
                return_value=registry.parse_units("meter"),
            ),
            patch(
                "pozo.units._lasio.remove_prefix_number",
                return_value="Test description",
            ),
            patch(
                "pozo.units._table.generate_html_table",
                return_value="<table>test</table>",
            ),
            patch("pozo.units.display.show_content") as mock_show_content,
        ):
            check_las(las_file, html=True, div_id=custom_div_id)

            call_args = mock_show_content.call_args
            assert (
                f'<div id="{custom_div_id}"><table>test</table></div>'
                in call_args[0][0]
            )


# okay
class TestParseUnitSafe:
    """Test the parse_unit_safe function."""

    def test_parse_unit_safe_valid_unit(self) -> None:
        """Test parse_unit_safe with valid unit string."""
        result = parse_unit_safe("meter")
        assert isinstance(result, pint.Unit)
        assert str(result) == "meter"

    def test_parse_unit_safe_valid_unit_abbreviation(self) -> None:
        """Test parse_unit_safe with valid unit abbreviation."""
        result = parse_unit_safe("m")
        assert isinstance(result, pint.Unit)
        assert str(result) == "meter"

    def test_parse_unit_safe_empty_string_dimensionless(self) -> None:
        """Test parse_unit_safe with empty string returns dimensionless."""
        result = parse_unit_safe("")
        assert isinstance(result, pint.Unit)
        assert result.dimensionless

    def test_parse_unit_safe_invalid_unit_returns_none(self) -> None:
        """Test parse_unit_safe with invalid unit returns None."""
        result = parse_unit_safe("invalid_unit_xyz")
        assert result is None

    def test_parse_unit_safe_complex_unit(self) -> None:
        """Test parse_unit_safe with complex unit."""
        result = parse_unit_safe("kg/m^3")
        assert isinstance(result, pint.Unit)

    def test_parse_unit_safe_pint_instance_raises_error(self) -> None:
        """Test parse_unit_safe with pint instance raises AttributeError."""
        pint_unit = registry.parse_units("meter")
        with pytest.raises(AttributeError):
            parse_unit_safe(pint_unit)


class TestParseUnitFromContext:
    """Test the parse_unit_from_context function."""

    def test_parse_unit_from_context_valid_args(self) -> None:
        """Test parse_unit_from_context with valid arguments."""
        mnemonic = "DEPTH"
        las_unit = "M"
        data = [1.0, 2.0, 3.0]

        result = parse_unit_from_context(mnemonic, las_unit, data)
        assert isinstance(result, pint.Unit)

    # Pendiente ajustar el control de retorno de la función
    def test_parse_unit_from_context_fallback_to_las_unit(self) -> None:
        """Test parse_unit_from_context falls back to las_unit when mapping fails."""
        mnemonic = "UNKNOWN_MNEMONIC"
        las_unit = "m"
        data = [1, 2, 3]

        result = parse_unit_from_context(mnemonic, las_unit, data)
        assert isinstance(result, pint.Unit)
        assert str(result) == "meter"

    def test_parse_unit_from_context_empty_string_dimensionless(self) -> None:
        """Test parse_unit_from_context with empty string returns dimensionless."""
        mnemonic = "UNKNOWN"
        las_unit = ""
        data = [1.0, 2.0, 3.0]

        result = parse_unit_from_context(mnemonic, las_unit, data)
        assert isinstance(result, pint.Unit)
        assert result.dimensionless

    # Pendiente ajustar el control de retorno de la función
    def test_parse_unit_from_context_invalid_units_returns_none(self) -> None:
        """Test parse_unit_from_context with invalid units returns None."""
        mnemonic = "UNKNOWN"
        las_unit = "completely_invalid_unit_xyz_123"
        data = [1.0, 2.0, 3.0]

        result = parse_unit_from_context(mnemonic, las_unit, data)
        assert result is None


class TestGetUnitFromCurve:
    """Test the get_unit_from_curve function."""

    def test_get_unit_from_curve_valid_curve(self) -> None:
        """Test get_unit_from_curve with valid Curve object."""
        curve = Mock()
        curve.mnemonic = "DEPTH"
        curve.unit = "M"
        curve.data = [1.0, 2.0, 3.0]

        result = get_unit_from_curve(curve)
        assert result is not None
        assert isinstance(result, pint.Unit)

    def test_get_unit_from_curve_empty_unit_dimensionless(self) -> None:
        """Test get_unit_from_curve with empty unit returns dimensionless."""
        curve = Mock()
        curve.mnemonic = "UNKNOWN"
        curve.unit = ""
        curve.data = [1.0, 2.0, 3.0]

        result = get_unit_from_curve(curve)
        assert result is not None
        assert isinstance(result, pint.Unit)
        assert result.dimensionless

    def test_get_unit_from_curve_pint_instance_raises_error(self) -> None:
        """Test get_unit_from_curve with pint instance raises AttributeError."""
        pint_unit = registry.parse_units("meter")
        with pytest.raises(AttributeError):
            get_unit_from_curve(pint_unit)


# pero unit to las solo funciona si ya hicimos un las to unit
class TestParseUnitToLas:
    """Test the parse_unit_to_las function."""

    def test_parse_unit_to_las_valid_args_pint_unit(self) -> None:
        """Test parse_unit_to_las with valid mnemonic and pint Unit."""
        mnemonic = "DEPTH"
        pint_unit = registry.parse_units("meter")

        result = parse_unit_to_las(mnemonic, pint_unit)
        assert result is not None
        assert isinstance(result, str)

    def test_parse_unit_to_las_valid_args_string_unit(self) -> None:
        """Test parse_unit_to_las with valid mnemonic and string unit."""
        mnemonic = "DEPTH"
        pint_unit = "meter"

        result = parse_unit_to_las(mnemonic, pint_unit)
        assert result is not None
        assert isinstance(result, str)

    def test_parse_unit_to_las_invalid_unit_raises_error(self) -> None:
        """Test parse_unit_to_las with invalid unit raises pint.UndefinedUnitError."""
        with pytest.raises(pint.UndefinedUnitError):
            parse_unit_to_las("DEPTH", "invalid_unit_xyz")
