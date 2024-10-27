# Veritas

Semver-based version specifications and requirement parsing.

## Usage

This package provides support for partial specifications of [Semver 2.0.0](https://semver.org/) versions and the ability to define a set of requirements.

### Versions

We make use of the [`semver`](https://pypi.org/project/semver) package to handle parsing of fully qualified Semver versions.
You can import their definition of a `Version` and declare Semver versions.

```python
from vertias import Version

ver_a = Version.parse("1.2.3")
print(ver_a)
# 1.2.3

print(repr(ver_a))
# Version(major=1, minor=2, patch=3, prerelease=None, build=None)
```

### Version Specifications

Version specifications define a single constraint that we expect to be true for a given version.

```python
from veritas import VersionSpec

spec_a = VersionSpec.parse(">1.2")
print(spec_a)
# >1.2

print(repr(spec_a))
# VersionSpec(op=<VersionOperation.GT: '>'>, major=1, minor=2, patch=None, prerelease=None, build=None)
```

### Version Requirements
