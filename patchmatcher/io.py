import json
from pathlib import Path

from .geometry import Circle, Rectangle


def load_json_input(path: Path) -> Rectangle:
    data = json.loads(path.read_text())
    return Rectangle(
        width=data["width"],
        height=data["height"],
        cx=data["cx"],
        cy=data["cy"],
    )


def write_json_output(path: Path, rect: Rectangle, hole: Circle) -> None:
    out = {
        "rectangle": {
            "width": rect.width,
            "height": rect.height,
            "cx": rect.cx,
            "cy": rect.cy,
        },
        "center_hole": {
            "radius": hole.radius,
            "cx": hole.cx,
            "cy": hole.cy,
        },
    }
    path.write_text(json.dumps(out, indent=2))


def write_dxf(path: Path, rect: Rectangle, hole: Circle) -> None:
    x1 = rect.cx - rect.width / 2
    y1 = rect.cy - rect.height / 2
    x2 = rect.cx + rect.width / 2
    y2 = rect.cy + rect.height / 2

    dxf = f"""0
SECTION
2
ENTITIES
0
LWPOLYLINE
8
0
90
4
70
1
10
{x1}
20
{y1}
10
{x2}
20
{y1}
10
{x2}
20
{y2}
10
{x1}
20
{y2}
0
CIRCLE
8
0
10
{hole.cx}
20
{hole.cy}
40
{hole.radius}
0
ENDSEC
0
EOF
"""
    path.write_text(dxf)


def dxf_to_string(rect: Rectangle, hole: Circle) -> str:
    x1 = rect.cx - rect.width / 2
    y1 = rect.cy - rect.height / 2
    x2 = rect.cx + rect.width / 2
    y2 = rect.cy + rect.height / 2

    return f"""0
SECTION
2
ENTITIES
0
LWPOLYLINE
8
0
90
4
70
1
10
{x1}
20
{y1}
10
{x2}
20
{y1}
10
{x2}
20
{y2}
10
{x1}
20
{y2}
0
CIRCLE
8
0
10
{hole.cx}
20
{hole.cy}
40
{hole.radius}
0
ENDSEC
0
EOF
"""
