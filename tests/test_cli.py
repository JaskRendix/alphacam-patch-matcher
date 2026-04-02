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


def test_cli_butterfly_custom_table(tmp_path):
    toml_path = tmp_path / "custom.toml"
    toml_path.write_text(
        """
        [W1]
        diam1 = 0.05
        diam2 = 0.05
        circ_offset = 0.35
        line1 = 0.6
        offset = 0.2
        angle = 9
        z_bottom = -0.5
        radius1 = 0
        radius2 = 0
        """
    )

    result = subprocess.run(
        [
            "python",
            "-m",
            "patchmatcher",
            "butterfly",
            "W1",
            "--table",
            str(toml_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Butterfly W1:" in result.stdout
    assert "diam1:" in result.stdout


def test_cli_butterfly_invalid_table(tmp_path):
    toml_path = tmp_path / "bad.toml"
    toml_path.write_text("not even toml")

    result = subprocess.run(
        [
            "python",
            "-m",
            "patchmatcher",
            "butterfly",
            "W1",
            "--table",
            str(toml_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Failed to load butterfly table" in result.stdout
