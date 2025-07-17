"""Tests for pozo.units.si_pint.config module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pint
import pytest

from pozo.units.si_pint.config import add_to_pint, pint_map


class TestAddToPint:
    """Test the add_to_pint function."""

    def test_add_to_pint_with_valid_registry(self) -> None:
        """Test add_to_pint with a valid registry instance."""
        registry = pint.get_application_registry()

        gamma_unit = registry.parse_units("gAPI")
        assert gamma_unit is not None
        assert str(gamma_unit) == "gamma_API_unit"

        porosity_unit = registry.parse_units("pu")
        assert porosity_unit is not None
        assert str(porosity_unit) == "porosity_unit"

        fraction_unit = registry.parse_units("fraction")
        assert fraction_unit is not None
        assert str(fraction_unit) == "of_1"

        legacy_porosity_unit = registry.parse_units("puAPI")
        assert legacy_porosity_unit is not None
        assert str(legacy_porosity_unit) == "legacy_api_porosity_unit"

    def test_add_to_pint_units_are_parseable(self) -> None:
        """Test that all units from pint_map are parseable after adding."""
        registry = pint.get_application_registry()
        expected_units = ["gAPI", "pu", "fraction", "puAPI"]

        for unit_str in expected_units:
            unit = registry.parse_units(unit_str)
            assert unit is not None
            assert isinstance(unit, pint.Unit)

    def test_add_to_pint_error_in_registry_define(self) -> None:
        """Test error handling when registry.define raises an exception."""
        mock_registry = Mock()
        mock_registry.define.side_effect = Exception("Registry define error")

        with pytest.raises(Exception, match="Registry define error"):
            add_to_pint(mock_registry)

    def test_add_to_pint_error_in_registry_define_specific_unit(self) -> None:
        """Test error handling when .define raises exception to specific unit."""
        mock_registry = Mock()
        mock_registry.define.side_effect = [
            None,
            Exception("Specific unit error"),
            None,
            None,
        ]

        with pytest.raises(Exception, match="Specific unit error"):
            add_to_pint(mock_registry)

    def test_add_to_pint_error_invalid_definition_format(self) -> None:
        """Test error handling when a definition has invalid format."""
        mock_registry = Mock()
        mock_registry.define.side_effect = pint.DefinitionSyntaxError(
            "Invalid definition"
        )

        with pytest.raises(pint.DefinitionSyntaxError, match="Invalid definition"):
            add_to_pint(mock_registry)

    def test_add_to_pint_error_undefined_unit_in_definition(self) -> None:
        """Test error handling when definition references undefined unit."""
        mock_registry = Mock()
        mock_registry.define.side_effect = pint.UndefinedUnitError(
            "Undefined unit in definition"
        )

        with pytest.raises(
            pint.UndefinedUnitError, match="Undefined unit in definition"
        ):
            add_to_pint(mock_registry)

    def test_add_to_pint_empty_pint_map(self) -> None:
        """Test add_to_pint with empty pint_map."""
        mock_registry = Mock()

        with patch("pozo.units.si_pint.config.pint_map", []):
            add_to_pint(mock_registry)
            mock_registry.define.assert_not_called()

    def test_add_to_pint_with_custom_pint_map(self) -> None:
        """Test add_to_pint with a custom pint_map."""
        mock_registry = Mock()
        custom_map = ["custom_unit = [Custom_Dimension] = cu"]

        with patch("pozo.units.si_pint.config.pint_map", custom_map):
            add_to_pint(mock_registry)
            mock_registry.define.assert_called_once_with(
                "custom_unit = [Custom_Dimension] = cu"
            )

    def test_pint_map_contains_expected_definitions(self) -> None:
        """Test that pint_map contains all expected unit definitions."""
        expected_definitions = [
            "gamma_API_unit = [Gamma_Ray_Tool_Response]  = gAPI",
            "porosity_unit = percent = pu",
            "of_1 = 100 * percent = fraction",
            "legacy_api_porosity_unit = [Legacy_API_Porosity_Unit] = puAPI",
        ]

        assert len(pint_map) == len(expected_definitions)

        for definition in expected_definitions:
            assert definition in pint_map

    def test_add_to_pint_registry_state_after_addition(self) -> None:
        """Test that registry state is correct after adding units."""
        registry = pint.get_application_registry()

        gamma_unit = registry.parse_units("gAPI")
        assert gamma_unit is not None

        porosity_unit = registry.parse_units("pu")
        assert porosity_unit is not None

        fraction_unit = registry.parse_units("fraction")
        assert fraction_unit is not None

        legacy_porosity_unit = registry.parse_units("puAPI")
        assert legacy_porosity_unit is not None

    def test_add_to_pint_units_have_correct_relationships(self) -> None:
        """Test that added units have correct relationships with existing units."""
        registry = pint.get_application_registry()

        porosity_unit = registry.parse_units("pu")
        percent_unit = registry.parse_units("percent")

        assert porosity_unit.dimensionality == percent_unit.dimensionality

        quantity_fraction = registry.Quantity(1, "fraction")

        exp_magnitude = 100
        assert quantity_fraction.to("pu").magnitude == exp_magnitude

    def test_add_to_pint_idempotent_behavior(self) -> None:
        """Test that calling add_to_pint multiple times doesn't cause issues."""
        registry = pint.get_application_registry()

        gamma_unit_first = registry.parse_units("gAPI")
        assert gamma_unit_first is not None

        try:
            add_to_pint(registry)

            gamma_unit_second = registry.parse_units("gAPI")
            assert gamma_unit_second is not None

        except pint.RedefinitionError:
            pass
