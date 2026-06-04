import json
from pathlib import Path

from .geometry import Circle, Rectangle

DXF_UNITS = {
    "unitless": 0,
    "in": 1,
    "ft": 2,
    "mi": 3,
    "mm": 4,
    "cm": 5,
    "m": 6,
}


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


def _dxf_string(
    rect: Rectangle, hole: Circle, *, scale: float = 1.0, units: str = "in"
) -> str:
    """
    Generate DXF content for a rectangle + center hole.
    scale: multiply all coordinates by this factor
    units: DXF $INSUNITS header (in, mm, cm, m, etc.)
    """

    if units not in DXF_UNITS:
        raise ValueError(f"Unsupported DXF unit: {units}")

    # Apply scale
    x1 = (rect.cx - rect.width / 2) * scale
    y1 = (rect.cy - rect.height / 2) * scale
    x2 = (rect.cx + rect.width / 2) * scale
    y2 = (rect.cy + rect.height / 2) * scale

    cx = rect.cx * scale
    cy = rect.cy * scale
    r = hole.radius * scale

    return f"""0
SECTION
2
HEADER
9
$INSUNITS
70
{DXF_UNITS[units]}
0
ENDSEC
0
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
{cx}
20
{cy}
40
{r}
0
ENDSEC
0
EOF
"""


def write_dxf(
    path: Path,
    rect: Rectangle,
    hole: Circle,
    *,
    scale: float = 1.0,
    units: str = "in",
) -> None:
    """
    Write DXF file with optional scaling and units.
    """
    dxf = _dxf_string(rect, hole, scale=scale, units=units)
    path.write_text(dxf)


def dxf_to_string(
    rect: Rectangle,
    hole: Circle,
    *,
    scale: float = 1.0,
    units: str = "in",
) -> str:
    """
    Return DXF as a string (used by API and tests).
    """
    return _dxf_string(rect, hole, scale=scale, units=units)
