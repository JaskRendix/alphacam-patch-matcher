import pytest

from patchmatcher.tables import PatchTable


def test_load_patch_table(top_patches):
    # Should load 70 entries for patchSizesTop.txt
    assert len(top_patches) == 70

    # Each entry is a Patch object with float width/height
    first = next(iter(top_patches))
    assert isinstance(first.width, float)
    assert isinstance(first.height, float)


def test_patchtable_iterates_over_patches(top_patches):
    patches = list(top_patches)
    assert len(patches) == 70
    assert all(hasattr(p, "width") and hasattr(p, "height") for p in patches)


from dataclasses import FrozenInstanceError


def test_patch_is_immutable(top_patches):
    patch = next(iter(top_patches))
    with pytest.raises(FrozenInstanceError):
        patch.width = 99


def test_patchtable_odd_number_of_lines(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("3.0\n5.0\n7.0\n")  # 3 lines → invalid

    with pytest.raises(ValueError):
        PatchTable.from_file(bad)


def test_patchtable_parses_floats(tmp_path):
    f = tmp_path / "floats.txt"
    f.write_text("3\n5\n")

    table = PatchTable.from_file(f)
    p = next(iter(table))

    assert isinstance(p.width, float)
    assert isinstance(p.height, float)
    assert p.width == 3.0
    assert p.height == 5.0


def test_patchtable_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")

    with pytest.raises(ValueError):
        PatchTable.from_file(f)


def test_patchtable_ignores_whitespace(tmp_path):
    f = tmp_path / "ws.txt"
    f.write_text("\n  3.0 \n\n 5.0 \n\n")

    table = PatchTable.from_file(f)
    p = next(iter(table))

    assert p.width == 3.0
    assert p.height == 5.0


def test_patchtable_bounds(tmp_path):
    f = tmp_path / "bounds.txt"
    f.write_text("3\n5\n10\n20\n")

    table = PatchTable.from_file(f)

    assert table.min_width == 3.0
    assert table.max_width == 10.0
    assert table.min_height == 5.0
    assert table.max_height == 20.0


def test_patchtable_validate_query_ok(tmp_path):
    f = tmp_path / "ok.txt"
    f.write_text("3\n5\n10\n20\n")

    table = PatchTable.from_file(f)

    # Should not raise
    table.validate_query(5, 10)


def test_patchtable_validate_query_outside(tmp_path):
    f = tmp_path / "badq.txt"
    f.write_text("3\n5\n10\n20\n")

    table = PatchTable.from_file(f)

    with pytest.raises(ValueError):
        table.validate_query(999, 999)


def test_patchtable_validate_query_with_tolerance(tmp_path):
    f = tmp_path / "tol.txt"
    f.write_text("10\n10\n")

    table = PatchTable.from_file(f)

    # tolerance = 2.0 → 12 is allowed
    table.validate_query(12, 12)


def test_patchtable_invalid_number(tmp_path):
    f = tmp_path / "invalid.txt"
    f.write_text("3.0\nnot_a_number\n")

    with pytest.raises(ValueError):
        PatchTable.from_file(f)


def test_patchtable_invalid_float_values(tmp_path):
    f = tmp_path / "naninf.txt"
    f.write_text("nan\n5\n")

    with pytest.raises(ValueError):
        PatchTable.from_file(f)

    f.write_text("inf\n5\n")
    with pytest.raises(ValueError):
        PatchTable.from_file(f)


def test_patchtable_invalid_float_values(tmp_path):
    f = tmp_path / "naninf.txt"
    f.write_text("nan\n5\n")

    with pytest.raises(ValueError):
        PatchTable.from_file(f)

    f.write_text("inf\n5\n")
    with pytest.raises(ValueError):
        PatchTable.from_file(f)
