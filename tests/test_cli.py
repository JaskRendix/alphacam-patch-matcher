import subprocess


def test_cli_match(tmp_path):
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

    result = subprocess.run(
        [
            "python",
            "-m",
            "patchmatcher",
            "match",
            "--width",
            "3.1",
            "--height",
            "4.9",
            "--table",
            str(table),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Matched patch: 3.0 x 5.0" in result.stdout


def test_cli_replace(tmp_path):
    table = tmp_path / "table.txt"
    table.write_text("3.0\n5.0\n")

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
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "New rectangle: 3.0 x 5.0 at (10.0, 20.0)" in result.stdout
    assert "Center hole: radius 0.05" in result.stdout


def test_cli_butterfly():
    result = subprocess.run(
        ["python", "-m", "patchmatcher", "butterfly", "W1"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Butterfly W1:" in result.stdout
    assert "diam1:" in result.stdout
