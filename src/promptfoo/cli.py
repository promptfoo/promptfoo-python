"""
CLI wrapper for promptfoo

This module provides a thin wrapper around the promptfoo Node.js CLI tool.
It executes the npx promptfoo command and passes through all arguments.
"""

import os
import platform
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

    Executes `npx promptfoo@latest <args>` and passes through all arguments.
    Exits with the same exit code as the underlying promptfoo command.
    """
    # Check for Node.js installation
    if not check_node_installed():
        print_installation_help()
        sys.exit(1)

    npx_path = shutil.which("npx")
    if not npx_path:
        print("ERROR: npx is not available. Please ensure Node.js is properly installed.", file=sys.stderr)
        sys.exit(1)

    # Build the command: npx promptfoo@latest <args>
    # Use @latest to always get the most recent version
    # Use the full path to npx for Windows compatibility
    cmd = [npx_path, "--yes", "promptfoo@latest"] + sys.argv[1:]

    # On Windows Python 3.9, we need shell=True for proper .cmd execution
    # On other platforms/versions, use shell=False to avoid npm cache issues
    is_windows_py39 = platform.system() == "Windows" and sys.version_info[:2] == (3, 9)

    try:
        # Execute the command and pass through stdio
        result = subprocess.run(
            cmd,
            env=os.environ.copy(),
            check=False,  # Don't raise exception on non-zero exit
            shell=is_windows_py39,  # Only use shell on Windows Python 3.9
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out after waiting too long", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to execute promptfoo: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
