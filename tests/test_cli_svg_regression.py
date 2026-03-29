import re
import subprocess


def extract_rect(svg_text):
    """Extract x, y, width, height from the <rect> element."""
    rect_match = re.search(
        r'<rect[^>]*x="([^"]+)"[^>]*y="([^"]+)"[^>]*width="([^"]+)"[^>]*height="([^"]+)"',
        svg_text,
    )
    assert rect_match, "No <rect> element found in SVG"
    x, y, w, h = map(float, rect_match.groups())
    return x, y, w, h


def extract_circle(svg_text):
    """Extract cx, cy, r from the <circle> element."""
    circ_match = re.search(
        r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*r="([^"]+)"',
        svg_text,
    )
    assert circ_match, "No <circle> element found in SVG"
    cx, cy, r = map(float, circ_match.groups())
    return cx, cy, r


def test_cli_svg_visual_regression(tmp_path):
    # Patch table
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

    # Output SVG file
    svg_out = tmp_path / "output.svg"

    # Run CLI
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

    assert result.returncode == 0
    assert svg_out.exists()

    svg = svg_out.read_text()

    # Extract geometry
    x, y, w, h = extract_rect(svg)
    cx, cy, r = extract_circle(svg)

    # Expected rectangle: 3.0 x 5.0 centered at (10, 20)
    assert w == 3.0
    assert h == 5.0
    assert x == 10 - 3.0 / 2
    assert y == 20 - 5.0 / 2

    # Expected hole: radius 0.05 at (10, 20)
    assert cx == 10
    assert cy == 20
    assert r == 0.05
