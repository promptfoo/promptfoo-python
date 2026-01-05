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
from typing import NoReturn, Union


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

    is_windows = platform.system() == "Windows"

    # Try to find a globally installed promptfoo first
    promptfoo_path = shutil.which("promptfoo")

    # Build the command
    # On Windows: use shell=True for .cmd file compatibility
    # On Unix: use shell=False for security
    cmd: Union[str, list[str]]
    use_shell: bool

    if is_windows:
        # Windows requires shell=True or cmd.exe to run .cmd files
        # Use subprocess list form which is safer than string form
        import shlex

        if promptfoo_path:
            args = ["promptfoo"] + sys.argv[1:]
        else:
            # Fall back to npx
            if not shutil.which("npx"):
                print("ERROR: promptfoo is not installed and npx is not available.", file=sys.stderr)
                print("Please install promptfoo globally: npm install -g promptfoo", file=sys.stderr)
                sys.exit(1)
            args = ["npx", "--yes", "promptfoo@latest"] + sys.argv[1:]

        # On Windows, use shell=True with properly quoted arguments
        cmd = " ".join(shlex.quote(arg) for arg in args)
        use_shell = True
    else:
        # Unix: use shell=False for security
        if promptfoo_path:
            cmd = [promptfoo_path] + sys.argv[1:]
        else:
            npx_path = shutil.which("npx")
            if not npx_path:
                print("ERROR: promptfoo is not installed and npx is not available.", file=sys.stderr)
                print("Please install promptfoo globally: npm install -g promptfoo", file=sys.stderr)
                sys.exit(1)
            cmd = [npx_path, "--yes", "promptfoo@latest"] + sys.argv[1:]
        use_shell = False

    try:
        # Execute the command
        result = subprocess.run(
            cmd,
            env=os.environ.copy(),
            check=False,  # Don't raise exception on non-zero exit
            shell=use_shell,
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
