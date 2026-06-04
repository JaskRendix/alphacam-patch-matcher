from .geometry import Circle, Rectangle
from .tables import Patch, PatchTable


class PatchMatcher:
    """
    Provides patch-matching and geometry-replacement operations
    using a PatchTable.
    """

    def __init__(self, patches: PatchTable):
        self.patches = patches

    def closest_patch(self, width: float, height: float) -> Patch:
        """
        Modern, correct patch selection:
        - Search all patches
        - Use Euclidean distance in (width, height) space
        - Deterministic tie-breaking via table order
        """
        patches_list = self.patches.patches

        def dist(p: Patch) -> float:
            return ((p.width - width) ** 2 + (p.height - height) ** 2) ** 0.5

        return min(patches_list, key=dist)

    def replace_geometry(
        self,
        geo: Rectangle,
        x_adjust: float = 0.0,
        y_adjust: float = 0.0,
    ) -> tuple[Rectangle, Circle]:
        """
        Replace a geometry with the closest patch rectangle.
        Returns:
            new Rectangle
            center Circle
        """
        patch = self.closest_patch(geo.width, geo.height)

        new_rect = Rectangle(
            width=patch.width + x_adjust,
            height=patch.height + y_adjust,
            cx=geo.cx,
            cy=geo.cy,
        )

        center_hole = Circle(radius=0.05, cx=geo.cx, cy=geo.cy)

        return new_rect, center_hole
