from .geometry import Circle, Rectangle


def rectangle_to_svg(
    rect: Rectangle, stroke="black", fill="none", stroke_width=0.1
) -> str:
    x = rect.cx - rect.width / 2
    y = rect.cy - rect.height / 2
    return (
        f'<rect x="{x}" y="{y}" width="{rect.width}" height="{rect.height}" '
        f'stroke="{stroke}" fill="{fill}" stroke-width="{stroke_width}" />'
    )


def circle_to_svg(circle: Circle, stroke="black", fill="none", stroke_width=0.1) -> str:
    return (
        f'<circle cx="{circle.cx}" cy="{circle.cy}" r="{circle.radius}" '
        f'stroke="{stroke}" fill="{fill}" stroke-width="{stroke_width}" />'
    )


def _compute_bounds(rect: Rectangle, hole: Circle):
    rx1 = rect.cx - rect.width / 2
    ry1 = rect.cy - rect.height / 2
    rx2 = rect.cx + rect.width / 2
    ry2 = rect.cy + rect.height / 2

    hx1 = hole.cx - hole.radius
    hy1 = hole.cy - hole.radius
    hx2 = hole.cx + hole.radius
    hy2 = hole.cy + hole.radius

    xmin = min(rx1, hx1)
    ymin = min(ry1, hy1)
    xmax = max(rx2, hx2)
    ymax = max(ry2, hy2)

    return xmin, ymin, xmax, ymax


def scene_to_svg(
    rect: Rectangle,
    hole: Circle,
    *,
    scale: float = 1.0,
    units: str = "px",
    stroke_width: float = 0.1,
) -> str:
    """
    Generate SVG for a rectangle + center hole.

    - Computes correct viewBox from geometry bounds
    - Supports scaling (e.g., inches→mm)
    - Supports arbitrary units (px, mm, cm, in)
    """

    if scale <= 0:
        raise ValueError(f"scale must be > 0, got {scale}")

    # Compute bounds
    xmin, ymin, xmax, ymax = _compute_bounds(rect, hole)

    # Apply scale
    vb_x = xmin * scale
    vb_y = ymin * scale
    vb_w = (xmax - xmin) * scale
    vb_h = (ymax - ymin) * scale

    # Build SVG header
    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" '
        f'width="{vb_w}{units}" height="{vb_h}{units}">'
    )

    # Body
    body = "\n  " + "\n  ".join(
        [
            rectangle_to_svg(
                rect, stroke="black", fill="none", stroke_width=stroke_width
            ),
            circle_to_svg(hole, stroke="red", fill="none", stroke_width=stroke_width),
        ]
    )

    return f"{header}\n{body}\n</svg>\n"
