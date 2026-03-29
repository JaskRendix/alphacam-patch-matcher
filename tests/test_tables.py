from patchmatcher.tables import load_patch_table


def test_load_patch_table(top_patches):
    # Should load 70 entries for patchSizesTop.txt
    assert len(top_patches) == 70

    # Each entry is a (width, height) tuple of floats
    w, h = top_patches[0]
    assert isinstance(w, float)
    assert isinstance(h, float)
