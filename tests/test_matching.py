from patchmatcher.matching import PatchMatcher


def test_closest_patch(top_patches):
    matcher = PatchMatcher(top_patches)

    patch = matcher.closest_patch(3.1, 4.9)

    assert isinstance(patch.width, float)
    assert isinstance(patch.height, float)


def test_replace_geometry(top_patches, sample_rect):
    matcher = PatchMatcher(top_patches)

    new_rect, hole = matcher.replace_geometry(sample_rect)

    assert new_rect.cx == sample_rect.cx
    assert new_rect.cy == sample_rect.cy

    assert hole.cx == sample_rect.cx
    assert hole.cy == sample_rect.cy

    assert new_rect.width > 0
    assert new_rect.height > 0


def test_closest_patch_exact_match(top_patches):
    matcher = PatchMatcher(top_patches)

    first = next(iter(top_patches))
    patch = matcher.closest_patch(first.width, first.height)

    assert patch.width == first.width
    assert patch.height == first.height


def test_replace_geometry_with_adjustments(top_patches, sample_rect):
    matcher = PatchMatcher(top_patches)

    new_rect, _ = matcher.replace_geometry(sample_rect, x_adjust=0.2, y_adjust=0.3)

    assert new_rect.width > sample_rect.width
    assert new_rect.height > sample_rect.height


def test_closest_patch_returns_patch_within_bounds(top_patches):
    matcher = PatchMatcher(top_patches)

    # Pick a value inside safe bounds
    # PatchTable bounds: min_w=1.25, max_w=18.0 (example)
    patch = matcher.closest_patch(10, 10)

    from patchmatcher.tables import Patch

    assert isinstance(patch, Patch)


def test_replace_geometry_types(top_patches, sample_rect):
    matcher = PatchMatcher(top_patches)

    new_rect, hole = matcher.replace_geometry(sample_rect)

    from patchmatcher.geometry import Circle, Rectangle

    assert isinstance(new_rect, Rectangle)
    assert isinstance(hole, Circle)


def test_patchmatcher_holds_reference(top_patches):
    matcher = PatchMatcher(top_patches)
    assert matcher.patches is top_patches
