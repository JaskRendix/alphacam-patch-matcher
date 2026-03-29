from patchmatcher.butterflies import BUTTERFLY_TABLE, get_butterfly_params


def test_butterfly_table_contains_all_codes():
    expected = {"W1", "W2", "W3", "W4", "W5", "W6", "W7", "B1", "B2"}
    assert expected.issubset(BUTTERFLY_TABLE.keys())


def test_get_butterfly_params():
    params = get_butterfly_params("W1")

    assert params.diam1 == 0.05
    assert params.offset > 0
    assert params.line1 > 0
