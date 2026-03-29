import subprocess


def test_cli_replace_svg_out(tmp_path):
    # Patch table
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

    # Output SVG file
    svg_out = tmp_path / "output.svg"

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
            "--svg-out",
            str(svg_out),
        ],
        capture_output=True,
        text=True,
    )

    # CLI executed successfully
    assert result.returncode == 0
    assert "Wrote SVG" in result.stdout

    # File was created
    assert svg_out.exists()

    # Validate SVG content
    text = svg_out.read_text()
    assert "<svg" in text
    assert "<rect" in text
    assert "<circle" in text
