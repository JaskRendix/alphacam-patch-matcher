import argparse
import json

import pytest

from patchmatcher import __main__ as cli


class FakePatch:
    def __init__(self, w, h):
        self.width = w
        self.height = h


class FakeMatchResult:
    def __init__(self, patch, distance=0.5, percentile=0.2):
        self.patch = patch
        self.distance = distance
        self.percentile = percentile


class FakeRect:
    def __init__(self, w, h, cx=0, cy=0):
        self.width = w
        self.height = h
        self.cx = cx
        self.cy = cy


class FakeHole:
    def __init__(self, cx=0, cy=0, radius=1.0):
        self.cx = cx
        self.cy = cy
        self.radius = radius


def test_cmd_match_basic(monkeypatch, capsys, tmp_path):
    fake_table = tmp_path / "table.json"
    fake_table.write_text("[]")

    class FakePatchTable:
        @staticmethod
        def from_file(path):
            return "fake-table"

    class FakeMatcher:
        def __init__(self, table):
            pass

        def closest_patch(self, w, h):
            return FakePatch(w, h)

    monkeypatch.setattr(cli, "PatchTable", FakePatchTable)
    monkeypatch.setattr(cli, "PatchMatcher", FakeMatcher)

    args = argparse.Namespace(
        width=10,
        height=20,
        table=fake_table,
        diagnostics=False,
        func=cli.cmd_match,
    )

    cli.cmd_match(args)
    out = capsys.readouterr().out
    assert "Matched patch: 10 x 20" in out


def test_cmd_match_diagnostics(monkeypatch, capsys, tmp_path):
    fake_table = tmp_path / "table.json"
    fake_table.write_text("[]")

    class FakePatchTable:
        @staticmethod
        def from_file(path):
            return "fake-table"

    class FakeMatcher:
        def __init__(self, table):
            pass

        def closest_patch_with_metrics(self, w, h):
            return FakeMatchResult(FakePatch(w, h), distance=0.33, percentile=0.1)

    monkeypatch.setattr(cli, "PatchTable", FakePatchTable)
    monkeypatch.setattr(cli, "PatchMatcher", FakeMatcher)

    args = argparse.Namespace(
        width=5,
        height=7,
        table=fake_table,
        diagnostics=True,
        func=cli.cmd_match,
    )

    cli.cmd_match(args)
    out = capsys.readouterr().out
    assert "Matched patch: 5 x 7" in out
    assert "Distance: 0.3300" in out
    assert "Confidence: 0.9000" in out


def test_cmd_replace_default_text(monkeypatch, capsys, tmp_path):
    fake_table = tmp_path / "table.json"
    fake_table.write_text("[]")

    class FakePatchTable:
        @staticmethod
        def from_file(path):
            return "fake-table"

    class FakeMatcher:
        def __init__(self, table):
            pass

        def replace_geometry(
            self, rect, x_adjust, y_adjust, hole_radius, diagnostics=False
        ):
            new_rect = FakeRect(rect.width + 1, rect.height + 2, rect.cx, rect.cy)
            hole = FakeHole(rect.cx, rect.cy, hole_radius)
            if diagnostics:
                return new_rect, hole, FakeMatchResult(FakePatch(1, 2))
            return new_rect, hole

    monkeypatch.setattr(cli, "PatchTable", FakePatchTable)
    monkeypatch.setattr(cli, "PatchMatcher", FakeMatcher)

    args = argparse.Namespace(
        width=10,
        height=20,
        cx=5,
        cy=6,
        table=fake_table,
        x_adjust=0,
        y_adjust=0,
        hole_radius=1.0,
        diagnostics=False,
        json_in=None,
        json_out=None,
        dxf_out=None,
        svg_out=None,
        func=cli.cmd_replace,
    )

    cli.cmd_replace(args)
    out = capsys.readouterr().out
    assert "New rectangle: 11 x 22" in out
    assert "Center hole: radius 1.0" in out


def test_cmd_replace_json_in(monkeypatch, capsys, tmp_path):
    fake_table = tmp_path / "table.json"
    fake_table.write_text("[]")

    json_in = tmp_path / "in.json"
    json_in.write_text(json.dumps({"width": 3, "height": 4, "cx": 1, "cy": 2}))

    json_out = tmp_path / "out.json"

    class FakePatchTable:
        @staticmethod
        def from_file(path):
            return "fake-table"

    class FakeMatcher:
        def __init__(self, table):
            pass

        def replace_geometry(
            self, rect, x_adjust, y_adjust, hole_radius, diagnostics=False
        ):
            return FakeRect(9, 9, 0, 0), FakeHole(0, 0, 1.0)

    monkeypatch.setattr(cli, "PatchTable", FakePatchTable)
    monkeypatch.setattr(cli, "PatchMatcher", FakeMatcher)
    monkeypatch.setattr(cli, "load_json_input", lambda p: FakeRect(3, 4, 1, 2))
    monkeypatch.setattr(
        cli, "write_json_output", lambda path, r, h: path.write_text("OK")
    )

    args = argparse.Namespace(
        width=None,
        height=None,
        cx=None,
        cy=None,
        table=fake_table,
        x_adjust=0,
        y_adjust=0,
        hole_radius=1.0,
        diagnostics=False,
        json_in=json_in,
        json_out=json_out,
        dxf_out=None,
        svg_out=None,
        func=cli.cmd_replace,
    )

    cli.cmd_replace(args)
    assert json_out.read_text() == "OK"


def test_cmd_replace_dxf(monkeypatch, capsys, tmp_path):
    fake_table = tmp_path / "table.json"
    fake_table.write_text("[]")

    dxf_out = tmp_path / "out.dxf"

    class FakePatchTable:
        @staticmethod
        def from_file(path):
            return "fake-table"

    class FakeMatcher:
        def __init__(self, table):
            pass

        def replace_geometry(
            self, rect, x_adjust, y_adjust, hole_radius, diagnostics=False
        ):
            return FakeRect(1, 2), FakeHole(0, 0)

    monkeypatch.setattr(cli, "PatchTable", FakePatchTable)
    monkeypatch.setattr(cli, "PatchMatcher", FakeMatcher)
    monkeypatch.setattr(cli, "write_dxf", lambda path, r, h: path.write_text("DXF"))

    args = argparse.Namespace(
        width=1,
        height=2,
        cx=0,
        cy=0,
        table=fake_table,
        x_adjust=0,
        y_adjust=0,
        hole_radius=1.0,
        diagnostics=False,
        json_in=None,
        json_out=None,
        dxf_out=dxf_out,
        svg_out=None,
        func=cli.cmd_replace,
    )

    cli.cmd_replace(args)
    assert dxf_out.read_text() == "DXF"


def test_cmd_replace_svg(monkeypatch, capsys, tmp_path):
    fake_table = tmp_path / "table.json"
    fake_table.write_text("[]")

    svg_out = tmp_path / "out.svg"

    class FakePatchTable:
        @staticmethod
        def from_file(path):
            return "fake-table"

    class FakeMatcher:
        def __init__(self, table):
            pass

        def replace_geometry(
            self, rect, x_adjust, y_adjust, hole_radius, diagnostics=False
        ):
            return FakeRect(1, 2), FakeHole(0, 0)

    monkeypatch.setattr(cli, "PatchTable", FakePatchTable)
    monkeypatch.setattr(cli, "PatchMatcher", FakeMatcher)
    monkeypatch.setattr(cli, "scene_to_svg", lambda r, h: "<svg></svg>")

    args = argparse.Namespace(
        width=1,
        height=2,
        cx=0,
        cy=0,
        table=fake_table,
        x_adjust=0,
        y_adjust=0,
        hole_radius=1.0,
        diagnostics=False,
        json_in=None,
        json_out=None,
        dxf_out=None,
        svg_out=svg_out,
        func=cli.cmd_replace,
    )

    cli.cmd_replace(args)
    assert svg_out.read_text() == "<svg></svg>"


def test_cmd_butterfly_builtin(monkeypatch, capsys):
    class FakeParams:
        def __init__(self):
            self.a = 1
            self.b = 2

    monkeypatch.setattr(cli, "get_butterfly_params", lambda code: FakeParams())

    args = argparse.Namespace(code="W1", table=None, func=cli.cmd_butterfly)
    cli.cmd_butterfly(args)

    out = capsys.readouterr().out
    assert "Butterfly W1:" in out
    assert "a: 1" in out
    assert "b: 2" in out


def test_cmd_butterfly_unknown_builtin(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "get_butterfly_params",
        lambda code: (_ for _ in ()).throw(ValueError("bad")),
    )

    args = argparse.Namespace(code="BAD", table=None, func=cli.cmd_butterfly)
    cli.cmd_butterfly(args)

    out = capsys.readouterr().out
    assert "bad" in out.lower()


def test_cmd_butterfly_custom_table(monkeypatch, capsys, tmp_path):
    table = tmp_path / "bf.toml"
    table.write_text("dummy")

    class FakeParams:
        def __init__(self, foo):
            self.foo = foo

    monkeypatch.setattr(cli, "load_butterfly_table", lambda p: {"X1": FakeParams(123)})

    args = argparse.Namespace(code="X1", table=table, func=cli.cmd_butterfly)
    cli.cmd_butterfly(args)

    out = capsys.readouterr().out
    assert "foo: 123" in out


def test_cmd_butterfly_custom_table_missing_code(monkeypatch, capsys, tmp_path):
    table = tmp_path / "bf.toml"
    table.write_text("dummy")

    monkeypatch.setattr(cli, "load_butterfly_table", lambda p: {"X1": {"foo": 123}})

    args = argparse.Namespace(code="BAD", table=table, func=cli.cmd_butterfly)
    cli.cmd_butterfly(args)

    out = capsys.readouterr().out
    assert "Unknown butterfly code" in out


def test_cmd_butterfly_table_load_error(monkeypatch, capsys, tmp_path):
    table = tmp_path / "bf.toml"
    table.write_text("dummy")

    monkeypatch.setattr(
        cli, "load_butterfly_table", lambda p: (_ for _ in ()).throw(Exception("boom"))
    )

    args = argparse.Namespace(code="X1", table=table, func=cli.cmd_butterfly)
    cli.cmd_butterfly(args)

    out = capsys.readouterr().out
    assert "Failed to load butterfly table" in out


def test_cmd_serve_missing_uvicorn(monkeypatch):
    monkeypatch.setattr(cli, "uvicorn", None)

    args = argparse.Namespace(host="127.0.0.1", port=8000, reload=False)

    with pytest.raises(SystemExit):
        cli.cmd_serve(args)


def test_cmd_serve_success(monkeypatch):
    called = {}

    def fake_run(app, host, port, reload):
        called["app"] = app
        called["host"] = host
        called["port"] = port
        called["reload"] = reload

    monkeypatch.setattr(cli, "uvicorn", type("U", (), {"run": fake_run}))

    args = argparse.Namespace(host="0.0.0.0", port=9000, reload=True)
    cli.cmd_serve(args)

    assert called["app"] == "patchmatcher.api:app"
    assert called["host"] == "0.0.0.0"
    assert called["port"] == 9000
    assert called["reload"] is True
