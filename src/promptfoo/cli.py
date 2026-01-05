"""
CLI wrapper for promptfoo

This module provides a thin wrapper around the promptfoo Node.js CLI tool.
It executes the npx promptfoo command and passes through all arguments.
"""

import contextlib
import os
import shutil
import sys
from typing import NoReturn


def check_node_installed() -> bool:
    """Check if Node.js is installed and available."""
    return shutil.which("node") is not None


def check_npx_installed() -> bool:
    """Check if npx is installed and available."""
    return shutil.which("npx") is not None


def print_installation_help() -> None:
    """Print helpful installation instructions for Node.js."""
    print("ERROR: promptfoo requires Node.js to be installed.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Please install Node.js:", file=sys.stderr)
    print("  - macOS: brew install node", file=sys.stderr)
    print("  - Ubuntu/Debian: sudo apt install nodejs npm", file=sys.stderr)
    print("  - Windows: Download from https://nodejs.org/", file=sys.stderr)
    print("", file=sys.stderr)
    print("Or use nvm (Node Version Manager):", file=sys.stderr)
    print("  https://github.com/nvm-sh/nvm", file=sys.stderr)


def main() -> NoReturn:
    """
    Main entry point for the promptfoo CLI wrapper.

    Uses os.execvp() to replace the current process with promptfoo.
    This is the standard Unix way to implement CLI wrappers - no subprocess overhead.
    """
    # Check for Node.js installation
    if not check_node_installed():
        print_installation_help()
        sys.exit(1)

    # Try to find a globally installed promptfoo first (fastest, most reliable)
    # This avoids npm cache issues and download delays with npx
    if shutil.which("promptfoo"):
        # Use the globally installed version
        # os.execvp replaces current process - never returns on success
        # If exec fails, fall through to npx
        with contextlib.suppress(OSError):
            os.execvp("promptfoo", ["promptfoo"] + sys.argv[1:])

    # Fall back to npx if no global installation or if global exec failed
    if not shutil.which("npx"):
        print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
        print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
        print("Or ensure Node.js is properly installed.", file=sys.stderr)
        sys.exit(1)

    # Use npx to run promptfoo
    # os.execvp replaces current process - never returns on success
    try:
        os.execvp("npx", ["npx", "-y", "promptfoo@latest"] + sys.argv[1:])
    except OSError as e:
        print(f"ERROR: Failed to execute promptfoo via npx: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
