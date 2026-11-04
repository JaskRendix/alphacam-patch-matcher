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
    distance_ratio: float  # Normalized distance metric where: 0.0 = exact match / 1.0 = as far away as the most distant candidate
    candidate_count: int  # Total candidates evaluated


@dataclass(frozen=True)
class ReplacementResult:
    """
    Result of geometry replacement containing the new rectangle, center hole,
    and optional match diagnostics.
    """

    rectangle: Rectangle
    hole: Circle
    diagnostics: MatchResult | None = None


def _validate_finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value}")


class PatchMatcher:
    """
    Provides patch-matching and geometry-replacement operations
    using a PatchTable.
    """

    def __init__(self, patches: PatchTable):
        self.patches = patches

    def _distance(self, p: Patch, width: float, height: float) -> float:
        return math.hypot(p.width - width, p.height - height)

    def _match(self, width: float, height: float) -> MatchResult:
        """
        Internal unified matching method to evaluate candidates and compute metrics.
        """
        self.patches.validate_query(width, height)
        patches_list = self.patches.patches

        if not patches_list:
            raise ValueError("Patch table is empty.")

        distances = [self._distance(p, width, height) for p in patches_list]

        # Pythonic idiom: find min using zip
        best_patch, best_distance = min(
            zip(patches_list, distances), key=lambda item: item[1]
        )

        max_distance = max(distances)
        distance_ratio = 0.0 if max_distance == 0 else best_distance / max_distance

        return MatchResult(
            patch=best_patch,
            distance=best_distance,
            distance_ratio=distance_ratio,
            candidate_count=len(patches_list),
        )

    def closest_patch(self, width: float, height: float) -> Patch:
        """
        Return only the best matching patch.
        """
        return self._match(width, height).patch

    def closest_patch_with_metrics(self, width: float, height: float) -> MatchResult:
        """
        Return rich MatchResult containing the patch, distance, and metrics.
        """
        return self._match(width, height)

    def replace_geometry(
        self,
        geo: Rectangle,
        x_adjust: float = 0.0,
        y_adjust: float = 0.0,
        hole_radius: float = 0.05,
        *,
        diagnostics: bool = False,
    ) -> ReplacementResult:
        """
        Replace a geometry with the closest patch rectangle.

        Returns:
            ReplacementResult containing the new Rectangle, center Circle,
            and optional MatchResult diagnostics.
        """
        _validate_finite(x_adjust, "x_adjust")
        _validate_finite(y_adjust, "y_adjust")
        _validate_finite(hole_radius, "hole_radius")
        if hole_radius <= 0:
            raise ValueError(f"hole_radius must be > 0, got {hole_radius}")

        # Perform match using the unified internal matcher
        match_result = self._match(geo.width, geo.height)

        # Compute and guard final dimensions against negative/zero results
        new_width = match_result.patch.width + x_adjust
        new_height = match_result.patch.height + y_adjust

        if new_width <= 0 or new_height <= 0:
            raise ValueError(
                f"Resulting patch dimensions must be positive, got width={new_width}, height={new_height}"
            )

        # Construct new rectangle with offsets
        new_rect = Rectangle(
            width=new_width,
            height=new_height,
            cx=geo.cx,
            cy=geo.cy,
        )

        # Center hole definition
        center_hole = Circle(radius=hole_radius, cx=geo.cx, cy=geo.cy)

        return ReplacementResult(
            rectangle=new_rect,
            hole=center_hole,
            diagnostics=match_result if diagnostics else None,
        )
