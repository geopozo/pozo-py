from pozo._utils import lasio_utils


class TestRemoveLasioSuffix:
    def test_remove_lasio_suffix_with_colon(self) -> None:
        """Test removing suffix when colon is present"""
        assert lasio_utils.remove_lasio_suffix("DEPTH:M") == "DEPTH"
        assert lasio_utils.remove_lasio_suffix("GR:API") == "GR"
        assert lasio_utils.remove_lasio_suffix("NPHI:V/V") == "NPHI"
        assert lasio_utils.remove_lasio_suffix("RHOB:G/C3") == "RHOB"

    def test_remove_lasio_suffix_without_colon(self) -> None:
        """Test that strings without colon are returned unchanged"""
        assert lasio_utils.remove_lasio_suffix("DEPTH") == "DEPTH"
        assert lasio_utils.remove_lasio_suffix("GR") == "GR"
        assert lasio_utils.remove_lasio_suffix("NPHI") == "NPHI"
        assert lasio_utils.remove_lasio_suffix("") == ""

    def test_remove_lasio_suffix_multiple_colons(self) -> None:
        """Test that only the first colon is used for splitting"""
        assert lasio_utils.remove_lasio_suffix("DEPTH:M:EXTRA") == "DEPTH"
        assert lasio_utils.remove_lasio_suffix("GR:API:UNIT") == "GR"

    def test_remove_lasio_suffix_colon_at_start(self) -> None:
        """Test edge case with colon at the start"""
        assert lasio_utils.remove_lasio_suffix(":SUFFIX") == ""

    def test_remove_lasio_suffix_colon_at_end(self) -> None:
        """Test edge case with colon at the end"""
        assert lasio_utils.remove_lasio_suffix("MNEMONIC:") == "MNEMONIC"


class TestRemovePrefixNumber:
    def test_remove_prefix_number_with_number(self) -> None:
        """Test removing prefix number when present"""
        assert lasio_utils.remove_prefix_number("1 Depth") == "Depth"
        assert lasio_utils.remove_prefix_number("123 Gamma Ray") == "Gamma Ray"
        assert (
            lasio_utils.remove_prefix_number("   42   Neutron Porosity")
            == "Neutron Porosity"
        )
        assert (
            lasio_utils.remove_prefix_number("  999  Bulk Density  ")
            == "Bulk Density  "
        )

    def test_remove_prefix_number_without_number(self) -> None:
        """Test that strings without prefix number are returned unchanged"""
        assert lasio_utils.remove_prefix_number("Depth") == "Depth"
        assert lasio_utils.remove_prefix_number("Gamma Ray") == "Gamma Ray"
        assert (
            lasio_utils.remove_prefix_number("Neutron Porosity") == "Neutron Porosity"
        )
        assert lasio_utils.remove_prefix_number("") == ""

    def test_remove_prefix_number_number_in_middle(self) -> None:
        """Test that numbers in the middle are not affected"""
        assert (
            lasio_utils.remove_prefix_number("Depth 123 meters") == "Depth 123 meters"
        )
        assert lasio_utils.remove_prefix_number("GR 456 API") == "GR 456 API"
