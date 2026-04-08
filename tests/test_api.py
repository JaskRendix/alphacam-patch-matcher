import json
from pathlib import Path

from fastapi.testclient import TestClient

from patchmatcher.api import app

client = TestClient(app)


def make_patch_table(tmp_path: Path) -> Path:
    table = tmp_path / "patches.txt"
    table.write_text(
        "\n".join(
            [
                "3",
                "5",
                "4",
                "6",
            ]
        )
        + "\n"
    )
    return table


def make_butterfly_table(tmp_path: Path) -> Path:
    table = tmp_path / "bfly.toml"
    table.write_text(
        """
[W9]
diam1 = 0.1
diam2 = 0.2
circ_offset = 0.3
line1 = 1.0
offset = 0.5
angle = 10
z_bottom = -0.5
radius1 = 0
radius2 = 0
"""
    )
    return table


def test_match_success(tmp_path):
    table = make_patch_table(tmp_path)

    response = client.post(
        "/match", params={"width": 3.1, "height": 4.9, "table": str(table)}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["matched_width"] == 3.0
    assert data["matched_height"] == 5.0


def test_match_missing_table():
    response = client.post(
        "/match", params={"width": 3, "height": 4, "table": "does_not_exist.txt"}
    )
    assert response.status_code == 400


def test_replace_success(tmp_path):
    table = make_patch_table(tmp_path)

    payload = {
        "width": 3.1,
        "height": 4.9,
        "cx": 10,
        "cy": 20,
        "table_path": str(table),
    }

    response = client.post("/replace", json=payload)
    assert response.status_code == 200

    data = response.json()
    rect = data["rectangle"]
    hole = data["center_hole"]

    assert rect["width"] == 3.0
    assert rect["height"] == 5.0
    assert rect["cx"] == 10
    assert rect["cy"] == 20

    assert hole["radius"] > 0
    assert hole["cx"] == 10
    assert hole["cy"] == 20


def test_replace_invalid_table():
    payload = {"width": 3, "height": 4, "cx": 0, "cy": 0, "table_path": "missing.txt"}
    response = client.post("/replace", json=payload)
    assert response.status_code == 400


def test_replace_dxf(tmp_path):
    table = make_patch_table(tmp_path)

    response = client.get(
        "/replace/dxf",
        params={"width": 3.1, "height": 4.9, "cx": 10, "cy": 20, "table": str(table)},
    )

    assert response.status_code == 200
    dxf = response.text

    assert "LWPOLYLINE" in dxf
    assert "CIRCLE" in dxf
    assert "EOF" in dxf


def test_replace_svg(tmp_path):
    table = make_patch_table(tmp_path)

    response = client.get(
        "/replace/svg",
        params={"width": 3.1, "height": 4.9, "cx": 10, "cy": 20, "table": str(table)},
    )

    assert response.status_code == 200
    svg = response.text

    assert "<svg" in svg
    assert "</svg>" in svg


def test_butterfly_default():
    response = client.get("/butterfly/W1")
    assert response.status_code == 200
    data = response.json()
    assert "diam1" in data
    assert "angle" in data


def test_butterfly_custom(tmp_path):
    table = make_butterfly_table(tmp_path)

    response = client.get("/butterfly/W9", params={"table": str(table)})

    assert response.status_code == 200
    data = response.json()

    assert data["diam1"] == 0.1
    assert data["angle"] == 10


def test_butterfly_invalid_code():
    response = client.get("/butterfly/NOPE")
    assert response.status_code == 404


def test_butterfly_custom_missing_code(tmp_path):
    table = make_butterfly_table(tmp_path)

    response = client.get("/butterfly/W123", params={"table": str(table)})

    assert response.status_code == 404
