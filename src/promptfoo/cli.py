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

    Tries to use globally installed promptfoo first, falls back to npx if needed.
    Exits with the same exit code as the underlying promptfoo command.
    """
    # Check for Node.js installation
    if not check_node_installed():
        print_installation_help()
        sys.exit(1)

    # Try to find a globally installed promptfoo first (fastest when it works)
    # This avoids npm cache issues and download delays with npx
    promptfoo_path = shutil.which("promptfoo")
    used_global = False

    if promptfoo_path:
        try:
            # Try the globally installed version first (preferred for speed)
            cmd = [promptfoo_path] + sys.argv[1:]
            result = subprocess.run(
                cmd,
                env=os.environ.copy(),
                stdin=subprocess.DEVNULL,  # Prevent prompts from blocking
                check=False,  # Don't raise exception on non-zero exit
                shell=False,  # Keep shell=False for security
            )
            sys.exit(result.returncode)
        except (OSError, PermissionError):
            # Global executable exists but failed to run (resource issues, permissions, etc.)
            # Fall through to npx fallback for reliability
            # Common on CI where executable may not be ready immediately after install
            used_global = True

    # Fall back to npx if:
    # 1. No global installation found, OR
    # 2. Global installation failed to execute (OSError, PermissionError, etc.)
    npx_path = shutil.which("npx")
    if not npx_path:
        if used_global:
            print("ERROR: Global promptfoo found but failed to execute, and npx is not available.", file=sys.stderr)
        else:
            print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
        print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
        print("Or ensure Node.js is properly installed.", file=sys.stderr)
        sys.exit(1)

    try:
        # Build and execute the npx fallback command
        # Use -y (short form) which is more widely supported than --yes
        cmd = [npx_path, "-y", "promptfoo@latest"] + sys.argv[1:]
        result = subprocess.run(
            cmd,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,  # Prevent prompts from blocking
            check=False,  # Don't raise exception on non-zero exit
            shell=False,  # Keep shell=False for security
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: Failed to execute promptfoo via npx: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
