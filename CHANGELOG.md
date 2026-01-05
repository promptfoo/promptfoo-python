# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-01-05

### Added

- Complete rewrite of the Python wrapper with actual working code
- Automatic detection of Node.js and npx availability
- Helpful error messages when Node.js is not installed
- Pass-through of all arguments to the underlying promptfoo CLI
- Support for environment variable configuration
- Proper exit code handling
- Graceful Ctrl+C handling

### Changed

- Now calls `npx promptfoo@latest` to always use the latest version
- Improved README with clear installation and usage instructions

### Fixed

- Package now actually works (previous version was non-functional)
- Proper module structure with `__init__.py` and `cli.py`
- Entry point correctly points to working code

## [0.1.0] - 2024-08-19

### Added

- Initial (non-functional) placeholder release
