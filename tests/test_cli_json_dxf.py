import json
import subprocess


def test_cli_replace_json_in(tmp_path):
    # Patch table
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

    # JSON input
    json_in = tmp_path / "input.json"
    json_in.write_text(json.dumps({"width": 3.1, "height": 4.9, "cx": 10, "cy": 20}))

    result = subprocess.run(
        [
            "python",
            "-m",
            "patchmatcher",
            "replace",
            "--json-in",
            str(json_in),
            "--table",
            str(table),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Should still print text output unless json-out or dxf-out is used
    assert "New rectangle: 3.0 x 5.0" in result.stdout
    assert "Center hole: radius 0.05" in result.stdout


def test_cli_replace_json_out(tmp_path):
    # Patch table
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

    # Output JSON file
    json_out = tmp_path / "output.json"

    result = subprocess.run(
        [
            "python",
            "-m",
            "patchmatcher",
            "replace",
            "--width",
            "3.1",
            "--height",
            "4.9",
            "--cx",
            "10",
            "--cy",
            "20",
            "--table",
            str(table),
            "--json-out",
            str(json_out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Wrote JSON output" in result.stdout

    # Validate JSON structure
    data = json.loads(json_out.read_text())
    assert data["rectangle"]["width"] == 3.0
    assert data["rectangle"]["height"] == 5.0
    assert data["rectangle"]["cx"] == 10
    assert data["rectangle"]["cy"] == 20
    assert data["center_hole"]["radius"] == 0.05


def test_cli_replace_dxf_out(tmp_path):
    # Patch table
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

    # Output DXF file
    dxf_out = tmp_path / "output.dxf"

    result = subprocess.run(
        [
            "python",
            "-m",
            "patchmatcher",
            "replace",
            "--width",
            "3.1",
            "--height",
            "4.9",
            "--cx",
            "10",
            "--cy",
            "20",
            "--table",
            str(table),
            "--dxf-out",
            str(dxf_out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Wrote DXF" in result.stdout

    # Validate DXF content exists and contains expected entities
    text = dxf_out.read_text()
    assert "LWPOLYLINE" in text
    assert "CIRCLE" in text
    assert "ENDSEC" in text
