import math
from dataclasses import dataclass

from .geometry import Circle, Rectangle
from .tables import Patch, PatchTable


@dataclass(frozen=True)
class MatchResult:
    """
    Rich diagnostic information about a patch match.
    """

    patch: Patch
    distance: float  # Euclidean distance to query
    percentile: float  # 0 = best match, 1 = worst match


class PatchMatcher:
    """
    Provides patch-matching and geometry-replacement operations
    using a PatchTable.
    """

    def __init__(self, patches: PatchTable):
        self.patches = patches

    def _distance(self, p: Patch, width: float, height: float) -> float:
        return math.hypot(p.width - width, p.height - height)

    def closest_patch(self, width: float, height: float) -> Patch:
        """
        Return only the patch (legacy behavior).
        """
        # Safety: ensure query is within reasonable bounds
        self.patches.validate_query(width, height)

        patches_list = self.patches.patches
        return min(patches_list, key=lambda p: self._distance(p, width, height))

    def closest_patch_with_metrics(self, width: float, height: float) -> MatchResult:
        """
        Return patch + distance + percentile.
        """
        self.patches.validate_query(width, height)

        patches_list = self.patches.patches
        distances = [self._distance(p, width, height) for p in patches_list]

        best_idx = min(range(len(patches_list)), key=lambda i: distances[i])
        best_patch = patches_list[best_idx]
        best_distance = distances[best_idx]

        # Percentile: where the best match sits relative to all distances
        max_distance = max(distances)
        percentile = 0.0 if max_distance == 0 else best_distance / max_distance

        return MatchResult(
            patch=best_patch,
            distance=best_distance,
            percentile=percentile,
        )

    def replace_geometry(
        self,
        geo: Rectangle,
        x_adjust: float = 0.0,
        y_adjust: float = 0.0,
        hole_radius: float = 0.05,
        *,
        diagnostics: bool = False,
    ):
        """
        Replace a geometry with the closest patch rectangle.

        Returns:
            - new Rectangle
            - center Circle
            - (optional) MatchResult if diagnostics=True
        """
        # Validate adjustments
        if math.isnan(x_adjust) or math.isinf(x_adjust):
            raise ValueError(f"x_adjust must be finite, got {x_adjust}")
        if math.isnan(y_adjust) or math.isinf(y_adjust):
            raise ValueError(f"y_adjust must be finite, got {y_adjust}")
        if hole_radius <= 0 or math.isnan(hole_radius) or math.isinf(hole_radius):
            raise ValueError(f"hole_radius must be > 0 and finite, got {hole_radius}")

        # Perform match
        if diagnostics:
            result = self.closest_patch_with_metrics(geo.width, geo.height)
            patch = result.patch
        else:
            patch = self.closest_patch(geo.width, geo.height)
            result = None

        # Construct new rectangle
        new_rect = Rectangle(
            width=patch.width + x_adjust,
            height=patch.height + y_adjust,
            cx=geo.cx,
            cy=geo.cy,
        )

        # Center hole
        center_hole = Circle(radius=hole_radius, cx=geo.cx, cy=geo.cy)

        if diagnostics:
            return new_rect, center_hole, result
        return new_rect, center_hole
