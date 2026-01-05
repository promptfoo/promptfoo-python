"""
CLI wrapper for promptfoo

This module provides a thin wrapper around the promptfoo Node.js CLI tool.
It executes the npx promptfoo command and passes through all arguments.
"""

import os
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

    Tries to use globally installed promptfoo first, falls back to npx.
    Exits with the same exit code as the underlying promptfoo command.
    """
    # Check for Node.js installation
    if not check_node_installed():
        print_installation_help()
        sys.exit(1)

    # Try to find a globally installed promptfoo first (fastest, most reliable)
    # This avoids npm cache issues and download delays with npx
    promptfoo_path = shutil.which("promptfoo")

    if promptfoo_path:
        # Use the globally installed version (preferred)
        cmd = [promptfoo_path] + sys.argv[1:]
    else:
        # Fall back to npx if no global installation
        # This is crucial for Windows where npx is actually npx.cmd
        # Using the full path works cross-platform with shell=False
        npx_path = shutil.which("npx")
        if not npx_path:
            print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
            print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
            print("Or ensure Node.js is properly installed.", file=sys.stderr)
            sys.exit(1)

        # Build the npx fallback command
        # Use -y (short form) which is more widely supported than --yes
        cmd = [npx_path, "-y", "promptfoo@latest"] + sys.argv[1:]

    try:
        # Execute the command and inherit stdio
        # stdin=DEVNULL prevents npx from blocking on prompts like "Ok to proceed? (y)"
        result = subprocess.run(
            cmd,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,  # Prevent prompts from blocking
            check=False,  # Don't raise exception on non-zero exit
            shell=False,  # Keep shell=False for security - works on all platforms with full path
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: Failed to execute promptfoo: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
