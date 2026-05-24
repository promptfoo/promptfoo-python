# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5](https://github.com/promptfoo/promptfoo-python/compare/promptfoo-v0.1.4...promptfoo-v0.1.5) (2026-05-24)


### Bug Fixes

* address telemetry and environment quality findings ([#50](https://github.com/promptfoo/promptfoo-python/issues/50)) ([9fd19f6](https://github.com/promptfoo/promptfoo-python/commit/9fd19f6426c769bfa57a24a8ad9bc2d8d686d9a0))
* resolve environment test quality findings ([#45](https://github.com/promptfoo/promptfoo-python/issues/45)) ([879bb2a](https://github.com/promptfoo/promptfoo-python/commit/879bb2ab530ef2a0b23f4773d8e32800b86d047e))

## [0.1.4](https://github.com/promptfoo/promptfoo-python/compare/promptfoo-v0.1.3...promptfoo-v0.1.4) (2026-04-04)


### Bug Fixes

* checkout release tag in build job and add manual re-publish trigger ([#30](https://github.com/promptfoo/promptfoo-python/issues/30)) ([5e0bd39](https://github.com/promptfoo/promptfoo-python/commit/5e0bd395e15d2f7b10512ead4fdcf6920847dcd0))
* clarify best-effort environment probe failures ([158007c](https://github.com/promptfoo/promptfoo-python/commit/158007c7f586155aa35cd7f7f68d513b38b7bb60))
* normalize Windows subprocess exit statuses ([#35](https://github.com/promptfoo/promptfoo-python/issues/35)) ([5e5a931](https://github.com/promptfoo/promptfoo-python/commit/5e5a931a0ec37fb1bb7cdd2dfea1674982ebb7d9))


### Documentation

* add CONTRIBUTING, CODE_OF_CONDUCT, and SECURITY files ([#32](https://github.com/promptfoo/promptfoo-python/issues/32)) ([414c2d5](https://github.com/promptfoo/promptfoo-python/commit/414c2d596e45bc9846e83796a66f81982c164cb5))

## [0.1.3](https://github.com/promptfoo/promptfoo-python/compare/promptfoo-v0.1.2...promptfoo-v0.1.3) (2026-02-24)


### Features

* add comprehensive environment detection for better Node.js installation guidance ([#12](https://github.com/promptfoo/promptfoo-python/issues/12)) ([4334a67](https://github.com/promptfoo/promptfoo-python/commit/4334a6720edf28404df273ac767ffbb1688f611b))
* add comprehensive type checking with mypy strict mode and pyright ([#20](https://github.com/promptfoo/promptfoo-python/issues/20)) ([e1aecb2](https://github.com/promptfoo/promptfoo-python/commit/e1aecb261ab200a3fab4dc0b67e1134c65d210d4))
* add PostHog telemetry for wrapper usage tracking ([#19](https://github.com/promptfoo/promptfoo-python/issues/19)) ([b08a0cf](https://github.com/promptfoo/promptfoo-python/commit/b08a0cf54880930845e1f7e80ceacf3b770f6072))
* add smoke tests for CLI integration testing ([#14](https://github.com/promptfoo/promptfoo-python/issues/14)) ([123088d](https://github.com/promptfoo/promptfoo-python/commit/123088dfd567b3aa19d7242fcd55845e9b997569))
* initial release of working Python wrapper ([3549052](https://github.com/promptfoo/promptfoo-python/commit/354905248a38665c8ee6cbd398f6559b036025a6))


### Bug Fixes

* configure release-please for initial 0.2.0 release ([#7](https://github.com/promptfoo/promptfoo-python/issues/7)) ([d5c95f9](https://github.com/promptfoo/promptfoo-python/commit/d5c95f9399e037d5046b3b3ce3bf527c58cc33b1))
* correct detection of wrapper shim on Windows/venv ([#5](https://github.com/promptfoo/promptfoo-python/issues/5)) ([79fbc2a](https://github.com/promptfoo/promptfoo-python/commit/79fbc2aac2abab84c143a6d591e730f053c54284))
* disable renovate lockFileMaintenance ([#26](https://github.com/promptfoo/promptfoo-python/issues/26)) ([5db1270](https://github.com/promptfoo/promptfoo-python/commit/5db1270d9900538808f31c757a545f3b7d97efc2))
* implement PROMPTFOO_VERSION, KeyboardInterrupt handling, nvm version ([#27](https://github.com/promptfoo/promptfoo-python/issues/27)) ([0d7d8f0](https://github.com/promptfoo/promptfoo-python/commit/0d7d8f0a3f33af4a2832795ec28ab9129ae35ef8))
* resolve CI failures in test workflow ([958cf01](https://github.com/promptfoo/promptfoo-python/commit/958cf013df6d7869041e037536b7a516fc0b5b46))
* use full npx path for Windows compatibility ([#4](https://github.com/promptfoo/promptfoo-python/issues/4)) ([ced6a8d](https://github.com/promptfoo/promptfoo-python/commit/ced6a8d3167a26af3fd8bbc76015199aefef636a))


### Documentation

* add comprehensive agent documentation ([#8](https://github.com/promptfoo/promptfoo-python/issues/8)) ([a6037ff](https://github.com/promptfoo/promptfoo-python/commit/a6037ff57c6bd7093f5b531456ead0cd0ab22dbd))

## [0.1.2](https://github.com/promptfoo/promptfoo-python/compare/promptfoo-v0.1.1...promptfoo-v0.1.2) (2026-01-11)


### Features

* add comprehensive environment detection for better Node.js installation guidance ([#12](https://github.com/promptfoo/promptfoo-python/issues/12)) ([4334a67](https://github.com/promptfoo/promptfoo-python/commit/4334a6720edf28404df273ac767ffbb1688f611b))
* add comprehensive type checking with mypy strict mode and pyright ([#20](https://github.com/promptfoo/promptfoo-python/issues/20)) ([8b10925](https://github.com/promptfoo/promptfoo-python/commit/8b1092581b2d1b30799fec021e5b4a30b9f4e79d))
* add PostHog telemetry for wrapper usage tracking ([#19](https://github.com/promptfoo/promptfoo-python/issues/19)) ([80b5c67](https://github.com/promptfoo/promptfoo-python/commit/80b5c6780eabccad428d2db82934b898135527e4))
* add smoke tests for CLI integration testing ([#14](https://github.com/promptfoo/promptfoo-python/issues/14)) ([8e653c4](https://github.com/promptfoo/promptfoo-python/commit/8e653c44bee6a18ef329420eb77658811b67eea1))

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
