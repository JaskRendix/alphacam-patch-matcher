import pytest

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


def test_closest_patch_with_metrics(top_patches):
    matcher = PatchMatcher(top_patches)

    result = matcher.closest_patch_with_metrics(3.1, 4.9)

    assert result.patch.width > 0
    assert result.patch.height > 0
    assert result.distance >= 0
    assert 0 <= result.percentile <= 1


def test_replace_geometry_with_diagnostics(top_patches, sample_rect):
    matcher = PatchMatcher(top_patches)

    new_rect, hole, diag = matcher.replace_geometry(
        sample_rect,
        diagnostics=True,
    )

    assert new_rect.width > 0
    assert new_rect.height > 0
    assert diag.distance >= 0
    assert 0 <= diag.percentile <= 1


def test_replace_geometry_custom_hole_radius(top_patches, sample_rect):
    matcher = PatchMatcher(top_patches)

    new_rect, hole = matcher.replace_geometry(
        sample_rect,
        hole_radius=0.25,
    )

    assert hole.radius == 0.25


def test_replace_geometry_invalid_hole_radius(top_patches, sample_rect):
    matcher = PatchMatcher(top_patches)

    with pytest.raises(ValueError):
        matcher.replace_geometry(sample_rect, hole_radius=-1)


def test_closest_patch_out_of_bounds(top_patches):
    matcher = PatchMatcher(top_patches)

    with pytest.raises(ValueError):
        matcher.closest_patch(999, 999)


def test_closest_patch_tie_breaking(top_patches):
    matcher = PatchMatcher(top_patches)

    # Pick a point exactly between two patches
    # The matcher must return the first one in table order
    p1 = next(iter(top_patches))
    p2 = list(top_patches)[1]

    mid_w = (p1.width + p2.width) / 2
    mid_h = (p1.height + p2.height) / 2

    patch = matcher.closest_patch(mid_w, mid_h)

    assert patch.width == p1.width
    assert patch.height == p1.height
