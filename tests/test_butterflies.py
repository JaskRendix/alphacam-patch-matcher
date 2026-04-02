from pathlib import Path

import pytest
import tomllib

from patchmatcher.butterflies import (
    BUTTERFLY_TABLE,
    ButterflyParams,
    get_butterfly_params,
    load_butterfly_table,
    validate_butterfly_section,
)


def test_butterfly_table_contains_all_codes():
    expected = {"W1", "W2", "W3", "W4", "W5", "W6", "W7", "B1", "B2"}
    assert expected.issubset(BUTTERFLY_TABLE.keys())


def test_get_butterfly_params():
    params = get_butterfly_params("W1")
    assert params.diam1 == 0.05
    assert params.offset > 0
    assert params.line1 > 0


def test_get_butterfly_params_invalid():
    with pytest.raises(ValueError):
        get_butterfly_params("NOPE")


def test_validator_missing_fields(tmp_path: Path):
    bad_toml = tmp_path / "bad.toml"
    bad_toml.write_text(
        """
        [W1]
        diam1 = 0.05
        # missing diam2, circ_offset, line1, offset, angle, z_bottom, radius1, radius2
        """
    )

    with pytest.raises(ValueError):
        load_butterfly_table(bad_toml)


def test_validator_extra_fields(tmp_path: Path):
    toml_path = tmp_path / "extra.toml"
    toml_path.write_text(
        """
        [W1]
        diam1 = 0.05
        diam2 = 0.05
        circ_offset = 0.35
        line1 = 0.6
        offset = 0.2
        angle = 9
        z_bottom = -0.5
        radius1 = 0
        radius2 = 0
        extra_field = 123
        """
    )

    data = tomllib.loads(toml_path.read_text())
    validate_butterfly_section("W1", data["W1"])

    with pytest.raises(TypeError):
        ButterflyParams(**data["W1"])


def test_validator_wrong_type(tmp_path: Path):
    toml_path = tmp_path / "wrong.toml"
    toml_path.write_text(
        """
        [W1]
        diam1 = "oops"
        diam2 = 0.05
        circ_offset = 0.35
        line1 = 0.6
        offset = 0.2
        angle = 9
        z_bottom = -0.5
        radius1 = 0
        radius2 = 0
        """
    )

    data = tomllib.loads(toml_path.read_text())
    validate_butterfly_section("W1", data["W1"])

    with pytest.raises(TypeError):
        ButterflyParams(**data["W1"])
