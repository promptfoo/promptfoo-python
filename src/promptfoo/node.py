"""Node.js runtime requirements shared by the CLI and installation help."""

import re
import subprocess

MIN_NODE_VERSION = (22, 22, 0)
MIN_NODE_VERSION_TEXT = ".".join(map(str, MIN_NODE_VERSION))


def get_node_version(node_path: str) -> tuple[int, int, int] | None:
    """Return the stable Node.js version, or None if it cannot be determined."""
    try:
        result = subprocess.run(
            [node_path, "--version"],
            capture_output=True,
            check=True,
            encoding="ascii",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    match = re.fullmatch(r"v([0-9]+)\.([0-9]+)\.([0-9]+)(?:\+[A-Za-z0-9.-]+)?", result.stdout.strip())
    if not match:
        return None
    return int(match[1]), int(match[2]), int(match[3])
