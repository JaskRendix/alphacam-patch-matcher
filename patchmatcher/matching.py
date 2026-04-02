from .geometry import Circle, Rectangle
from .tables import Patch, PatchTable


def closest_patch(width: float, height: float, patches: PatchTable) -> Patch:
    """
    Modern Python version of the VB6 search logic:
      1. Find closest width
      2. From that index onward, find closest height
    """
    patches_list = patches.patches

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
    geo: Rectangle,
    patches: PatchTable,
    x_adjust: float = 0.0,
    y_adjust: float = 0.0,
):
    """
    Replace a geometry with the closest patch rectangle.
    Returns:
        new Rectangle
        center Circle
    """
    patch = closest_patch(geo.width, geo.height, patches)

    new_rect = Rectangle(
        width=patch.width + x_adjust,
        height=patch.height + y_adjust,
        cx=geo.cx,
        cy=geo.cy,
    )

    center_hole = Circle(radius=0.05, cx=geo.cx, cy=geo.cy)

    return new_rect, center_hole
