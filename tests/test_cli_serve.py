import argparse

import pytest

from patchmatcher import __main__ as cli


def test_cli_serve(monkeypatch):
    called = {}

    # Fake uvicorn.run
    def fake_run(app, host, port, reload):
        called["app"] = app
        called["host"] = host
        called["port"] = port
        called["reload"] = reload

    # Monkeypatch the uvicorn imported inside cli module
    monkeypatch.setattr(cli, "uvicorn", type("FakeUvicorn", (), {"run": fake_run}))

    args = argparse.Namespace(
        host="0.0.0.0",
        port=9000,
        reload=False,
        func=cli.cmd_serve,
    )

    cli.cmd_serve(args)

    assert called["app"] == "patchmatcher.api:app"
    assert called["host"] == "0.0.0.0"
    assert called["port"] == 9000
    assert called["reload"] is False


def test_cli_serve_success(monkeypatch):
    called = {}

    # Fake uvicorn.run
    def fake_run(app, host, port, reload):
        called["app"] = app
        called["host"] = host
        called["port"] = port
        called["reload"] = reload

    # Monkeypatch the uvicorn imported inside cli module
    monkeypatch.setattr(cli, "uvicorn", type("FakeUvicorn", (), {"run": fake_run}))

    args = argparse.Namespace(
        host="0.0.0.0",
        port=9000,
        reload=False,
        func=cli.cmd_serve,
    )

    cli.cmd_serve(args)

    assert called["app"] == "patchmatcher.api:app"
    assert called["host"] == "0.0.0.0"
    assert called["port"] == 9000
    assert called["reload"] is False


def test_cli_serve_missing_uvicorn(monkeypatch):
    # Simulate uvicorn not installed
    monkeypatch.setattr(cli, "uvicorn", None)

    args = argparse.Namespace(
        host="127.0.0.1",
        port=8000,
        reload=False,
        func=cli.cmd_serve,
    )

    with pytest.raises(SystemExit) as e:
        cli.cmd_serve(args)

    msg = str(e.value)
    assert "FastAPI/uvicorn not installed" in msg
    assert "pip install 'patchmatcher[api]'" in msg
