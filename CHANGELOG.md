# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0]

### Added

- Adding functionality for VersionSpec and VersionRequirement
- Adding `compare` and `check` methods to `VersionRequirement`
- Adding support for prerelease and build wildcards

### Changed

- Updating package name to `veritas`
- Bumping to latest working mypy pre-commit hook
- Adding required dependencies and fixing configuration
- WIP work for prerelease and build definitions
- Updating .gitignore to ignore root-level python files
- Adding basic usage to README
- Adding some clarification on CI in CONTRIBUTING

### Fixed

- Addressing max VersionSpec constraints for VersionRequirement
