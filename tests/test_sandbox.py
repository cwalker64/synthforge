"""Tests for the subprocess sandbox."""

from synthforge.eval.sandbox import run_in_sandbox


def test_passing_candidate() -> None:
    result = run_in_sandbox(
        "def add(a, b):\n    return a + b\n",
        ["assert add(2, 3) == 5"],
    )
    assert not result.timed_out
    assert result.outcomes[0]["passed"] is True


def test_failing_assertion() -> None:
    result = run_in_sandbox(
        "def add(a, b):\n    return a - b\n",
        ["assert add(2, 3) == 5"],
    )
    assert result.outcomes[0]["passed"] is False
    assert result.outcomes[0]["error"]


def test_program_with_error_fails_all_tests() -> None:
    result = run_in_sandbox(
        "def add(a, b):\n    return undefined_name\n",
        ["assert add(1, 1) == 2", "assert add(2, 2) == 4"],
    )
    # The candidate imports/defines fine, error only surfaces when called.
    assert all(o["passed"] is False for o in result.outcomes)


def test_syntax_error_fails_all_tests() -> None:
    result = run_in_sandbox(
        "def broken(:\n    pass\n",
        ["assert True"],
    )
    assert result.outcomes[0]["passed"] is False


def test_timeout_is_reported() -> None:
    result = run_in_sandbox(
        "def spin():\n    while True:\n        pass\n",
        ["spin()"],
        timeout=1.0,
    )
    assert result.timed_out is True
    assert result.outcomes[0]["passed"] is False


def test_reliability_guard_blocks_file_removal() -> None:
    # os.remove is disabled inside the sandbox, so calling it raises and the
    # test that relies on it is reported as failed rather than deleting a file.
    source = "import os\n\ndef wipe(path):\n    os.remove(path)\n    return True\n"
    result = run_in_sandbox(source, ["assert wipe('/tmp/whatever') is True"])
    assert result.outcomes[0]["passed"] is False
