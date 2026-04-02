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
        Modern Python version of the VB6 search logic:
          1. Find closest width
          2. From that index onward, find closest height
        """
        patches_list = self.patches.patches

        # Step 1: closest width
        best_w_idx = min(
            range(len(patches_list)),
            key=lambda i: abs(patches_list[i].width - width),
        )

        # Step 2: closest height starting from best_w_idx
        best_idx = min(
            range(best_w_idx, len(patches_list)),
            key=lambda i: abs(patches_list[i].height - height),
        )

        return patches_list[best_idx]

    def replace_geometry(
        self,
        geo: Rectangle,
        x_adjust: float = 0.0,
        y_adjust: float = 0.0,
    ):
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
