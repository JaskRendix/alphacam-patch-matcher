import json

import pytest

from patchmatcher.geometry import Circle, Rectangle
from patchmatcher.io import dxf_to_string, load_json_input, write_dxf, write_json_output


def test_load_json_input(tmp_path):
    p = tmp_path / "in.json"
    p.write_text(
        json.dumps(
            {
                "width": 10,
                "height": 20,
                "cx": 3,
                "cy": 4,
            }
        )
    )

    rect = load_json_input(p)
    assert rect.width == 10
    assert rect.height == 20
    assert rect.cx == 3
    assert rect.cy == 4


def test_write_json_output(tmp_path):
    p = tmp_path / "out.json"

    rect = Rectangle(width=10, height=20, cx=5, cy=6)
    hole = Circle(cx=5, cy=6, radius=1.5)

    write_json_output(p, rect, hole)

    data = json.loads(p.read_text())
    assert data["rectangle"]["width"] == 10
    assert data["rectangle"]["height"] == 20
    assert data["center_hole"]["radius"] == 1.5


def test_dxf_to_string_basic():
    rect = Rectangle(width=10, height=20, cx=0, cy=0)
    hole = Circle(cx=0, cy=0, radius=2)

    dxf = dxf_to_string(rect, hole, scale=1.0, units="in")

    # Basic DXF structure checks
    assert "SECTION" in dxf
    assert "LWPOLYLINE" in dxf
    assert "CIRCLE" in dxf
    assert "$INSUNITS" in dxf
    assert "70" in dxf  # DXF header code


def test_dxf_to_string_invalid_units():
    rect = Rectangle(width=10, height=20, cx=0, cy=0)
    hole = Circle(cx=0, cy=0, radius=2)

    with pytest.raises(ValueError):
        dxf_to_string(rect, hole, units="invalid-unit")


def test_write_dxf(tmp_path):
    p = tmp_path / "shape.dxf"

    rect = Rectangle(width=10, height=20, cx=0, cy=0)
    hole = Circle(cx=0, cy=0, radius=2)

    write_dxf(p, rect, hole, scale=2.0, units="mm")

    text = p.read_text()
    assert "LWPOLYLINE" in text
    assert "CIRCLE" in text
    assert "$INSUNITS" in text
