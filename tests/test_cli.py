"""End-to-end tests for the command-line interface."""

from synthforge.cli import main


def test_run_bundled_suite_succeeds(capsys) -> None:
    code = main(["run"])
    out = capsys.readouterr().out
    assert code == 0
    assert "SOLVED" in out


def test_run_json_format(capsys) -> None:
    code = main(["run", "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    assert out.strip().startswith("[")
    assert '"solved": true' in out


def test_synths_lists_backends(capsys) -> None:
    code = main(["synths"])
    out = capsys.readouterr().out
    assert code == 0
    assert "template" in out
    assert "fixture" in out


def test_unknown_synthesizer_reports_error(capsys) -> None:
    code = main(["run", "--synthesizer", "nope"])
    err = capsys.readouterr().err
    assert code == 2
    assert "error:" in err


def test_no_command_prints_help(capsys) -> None:
    code = main([])
    out = capsys.readouterr().out
    assert code == 0
    assert "usage" in out.lower()
