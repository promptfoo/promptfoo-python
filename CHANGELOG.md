# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1](https://github.com/promptfoo/promptfoo-python/compare/promptfoo-v0.1.0...promptfoo-v0.1.1) (2026-01-06)


### Features

* initial release of working Python wrapper ([3549052](https://github.com/promptfoo/promptfoo-python/commit/354905248a38665c8ee6cbd398f6559b036025a6))


### Bug Fixes

* configure release-please for initial 0.2.0 release ([#7](https://github.com/promptfoo/promptfoo-python/issues/7)) ([d5c95f9](https://github.com/promptfoo/promptfoo-python/commit/d5c95f9399e037d5046b3b3ce3bf527c58cc33b1))
* correct detection of wrapper shim on Windows/venv ([#5](https://github.com/promptfoo/promptfoo-python/issues/5)) ([79fbc2a](https://github.com/promptfoo/promptfoo-python/commit/79fbc2aac2abab84c143a6d591e730f053c54284))
* resolve CI failures in test workflow ([958cf01](https://github.com/promptfoo/promptfoo-python/commit/958cf013df6d7869041e037536b7a516fc0b5b46))
* use full npx path for Windows compatibility ([#4](https://github.com/promptfoo/promptfoo-python/issues/4)) ([ced6a8d](https://github.com/promptfoo/promptfoo-python/commit/ced6a8d3167a26af3fd8bbc76015199aefef636a))


### Documentation

* add comprehensive agent documentation ([#8](https://github.com/promptfoo/promptfoo-python/issues/8)) ([a6037ff](https://github.com/promptfoo/promptfoo-python/commit/a6037ff57c6bd7093f5b531456ead0cd0ab22dbd))

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
