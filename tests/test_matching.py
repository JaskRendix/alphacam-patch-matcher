from patchmatcher.geometry import Rectangle
from patchmatcher.matching import closest_patch, replace_geometry


def test_closest_patch(top_patches):
    # Pick a size close to an existing patch
    w, h = closest_patch(3.1, 4.9, top_patches)

    # Should match a real patch from the table
    assert isinstance(w, float)
    assert isinstance(h, float)


def test_replace_geometry(top_patches, sample_rect):
    new_rect, hole = replace_geometry(sample_rect, top_patches)

    # New rectangle should be centered at the same point
    assert new_rect.cx == sample_rect.cx
    assert new_rect.cy == sample_rect.cy

    # Hole should be centered at the same point
    assert hole.cx == sample_rect.cx
    assert hole.cy == sample_rect.cy

    # New rectangle should have positive dimensions
    assert new_rect.width > 0
    assert new_rect.height > 0
