from .geometry import Rectangle, Circle

PatchSize = tuple[float, float]


def closest_patch(width: float, height: float, patches: list[PatchSize]) -> PatchSize:
    """
    Modern Python version of the VB6 search logic:
      1. Find closest width
      2. From that index onward, find closest height
    """
    # Step 1: closest width
    best_w_idx = min(
        range(len(patches)),
        key=lambda i: abs(patches[i][0] - width)
    )

    # Step 2: closest height starting from best_w_idx
    best_idx = min(
        range(best_w_idx, len(patches)),
        key=lambda i: abs(patches[i][1] - height)
    )

    return patches[best_idx]


def replace_geometry(
    geo: Rectangle,
    patches: list[PatchSize],
    x_adjust: float = 0.0,
    y_adjust: float = 0.0,
):
    """
    Replace a geometry with the closest patch rectangle.
    Returns:
        new Rectangle
        center Circle
    """
    w, h = closest_patch(geo.width, geo.height, patches)

    new_rect = Rectangle(
        width=w + x_adjust,
        height=h + y_adjust,
        cx=geo.cx,
        cy=geo.cy,
    )

    center_hole = Circle(radius=0.05, cx=geo.cx, cy=geo.cy)

    return new_rect, center_hole
