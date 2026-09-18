"""Tests for reading the Node.js version reported by the executable."""

import subprocess
from unittest.mock import MagicMock

import pytest

from promptfoo.node import get_node_version


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("v20.20.2\n", (20, 20, 2)),
        ("v22.21.9\n", (22, 21, 9)),
        ("v22.22.0\r\n", (22, 22, 0)),
        ("v22.22.1\n", (22, 22, 1)),
        ("v24.0.0\n", (24, 0, 0)),
        ("v26.1.0+custom.1\n", (26, 1, 0)),
        ("v22.22.0-rc.1\n", None),
        ("v26.0.0-nightly20260507\n", None),
        ("22.22.0", None),
        ("v22.22", None),
        ("v22.22.0\nunexpected", None),
        ("unexpected", None),
        ("", None),
    ],
)
def test_get_node_version(monkeypatch: pytest.MonkeyPatch, output: str, expected: tuple[int, int, int] | None) -> None:
    """Parse stable versions and leave malformed or prerelease output unsupported."""
    run = MagicMock(return_value=subprocess.CompletedProcess([], 0, stdout=output))
    monkeypatch.setattr(subprocess, "run", run)

    assert get_node_version("/path with spaces/node") == expected
    run.assert_called_once_with(
        ["/path with spaces/node", "--version"],
        capture_output=True,
        check=True,
        encoding="ascii",
        errors="replace",
        timeout=5,
    )


@pytest.mark.parametrize(
    "error",
    [OSError("not executable"), subprocess.CalledProcessError(1, ["node"]), subprocess.TimeoutExpired(["node"], 5)],
)
def test_get_node_version_failure(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    """A broken or unresponsive executable does not escape into the wrapper."""
    monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=error))

    assert get_node_version("node") is None
