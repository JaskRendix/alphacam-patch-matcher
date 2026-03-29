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


def scene_to_svg(rect: Rectangle, hole: Circle, width=None, height=None) -> str:
    if width is None:
        width = rect.width * 2
    if height is None:
        height = rect.height * 2

    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )

    body = "\n  " + "\n  ".join(
        [
            rectangle_to_svg(rect, stroke="black", fill="none"),
            circle_to_svg(hole, stroke="red", fill="none"),
        ]
    )

    return f"{header}\n{body}\n</svg>\n"
