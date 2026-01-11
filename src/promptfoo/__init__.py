"""
promptfoo - Python wrapper for the promptfoo CLI

This package provides a Python interface to the promptfoo TypeScript CLI tool.
It requires Node.js and npx to be installed on the system.

Usage:
    $ promptfoo --help
    $ promptfoo eval
    $ promptfoo redteam

For full documentation, visit: https://www.promptfoo.dev/docs
"""

__version__ = "0.1.2"
__all__ = ["__version__", "main"]

from .cli import main
