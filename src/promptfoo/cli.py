"""
CLI wrapper for promptfoo

This module provides a thin wrapper around the promptfoo Node.js CLI tool.
It executes the npx promptfoo command and passes through all arguments.
"""

import shutil
import subprocess
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

    Executes promptfoo using subprocess.run() with minimal configuration.
    """
    # Check for Node.js installation
    if not check_node_installed():
        print_installation_help()
        sys.exit(1)

    # Build command: try global promptfoo first, fall back to npx
    if shutil.which("promptfoo"):
        cmd = ["promptfoo"] + sys.argv[1:]
    elif shutil.which("npx"):
        cmd = ["npx", "-y", "promptfoo@latest"] + sys.argv[1:]
    else:
        print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
        print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
        print("Or ensure Node.js is properly installed.", file=sys.stderr)
        sys.exit(1)

    # Execute with absolute minimal configuration
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
