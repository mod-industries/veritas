# Veritas

Semver-based version specifications and requirement parsing.

## Usage

This package provides support for partial specifications of [Semver 2.0.0](https://semver.org/) versions and the ability to define a set of requirements.

### Versions

We make use of the [`semver`](https://pypi.org/project/semver) package to handle parsing of fully qualified Semver versions.
You can declare a fully qualified version using the `Version` class and compare them using the standard comparison operators.

```python
from vertias import Version

ver_a = Version.parse("1.2.3")
print(ver_a)
# 1.2.3

print(repr(ver_a))
# Version(major=1, minor=2, patch=3, prerelease=None, build=None)
```

### Version Specifications

Version specifications define a single constraint that we expect to be true for a given fully qualified version.

```python
from veritas import VersionSpec, Version

# Version must be greater than 1.2
VersionSpec.parse(">1.2").check(Version.parse("1.3.0")) # True

# Wildcards are also supported
VersionSpec.parse("1.2.*").check(Version.parse("1.2.0")) # True

# To determine the relationship between a version and a specification, use the `compare` method
VersionSpec.parse("<1").compare(Version.parse("1.0.0")) # -1
```

#### Version Specification Operators

The following operators are supported for version specifications:

- `^` Caret (major version)
- `~` Tilde (minor version)
- `=` Equal to
- `>` Greater than
- `>=` Greater than or equal to
- `<` Less than
- `<=` Less than or equal to

If no operator is provided, the specification is assumed to be an exact match.

### Version Requirements

Version requirements are a set of version specifications that must all be satisfied by a given version.

```python
from veritas import VersionRequirement, Version

# A single version specification can be used as a requirement
VersionRequirement.parse("=1.2").check(Version.parse("1.2.3")) # True

# Multiple version specifications can be combined using commas
VersionRequirement.parse(">1.2, <2.0").check(Version.parse("1.5.0")) # True

# Invalid version requirements will raise a ParseError
VersionRequirement.parse("<1.2, >2.0") # veritas.exceptions.ParseError

# To determine the relationship between a version and a requirement, use the `compare` method
VersionRequirement.parse("^1.3").compare(Version.parse("1.4.0")) # 1
```
