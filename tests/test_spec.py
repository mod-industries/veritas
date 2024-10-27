from string import printable

import pytest
from hypothesis import given
from hypothesis.strategies import from_regex, just, one_of
from semver import Version

from veritas.constants import VERSION_SPECIFICATION_PATTERN
from veritas.exceptions import ParseError
from veritas.spec import VersionSpec


@given(from_regex(VERSION_SPECIFICATION_PATTERN, alphabet=printable))
def test_VersionSpec_parse(specification: str):
    assert str(VersionSpec.parse(specification)) == specification


@given(
    one_of(
        just(""),  # Don't allow empty strings
        from_regex(r"\A([=~^><]|[><]=)\*\Z"),  # Don't allow operations with major wildcard
        from_regex(r"\A(\d+\.)+\Z"),  # Don't allow versions with missing parts
        from_regex(r"\A\d+(\.\d+){3,}\Z"),  # Don't allow versions with more than 3 parts
    )
)
def test_VersionSpec_parse_fails_on_invalid(specification: str):
    with pytest.raises(ParseError):
        VersionSpec.parse(specification)


@pytest.mark.parametrize(
    "pair",
    [
        ("*", (0, 0, 0)),
        ("1", (1, 0, 0)),
        ("1.*", (1, 0, 0)),
        ("1.2", (1, 2, 0)),
        ("1.2.*", (1, 2, 0)),
        ("1.2.3", (1, 2, 3)),
        ("1.2.3-alpha", (1, 2, 3)),
        ("1.2.3-alpha+build", (1, 2, 3)),
        ("^1", (1, 0, 0)),
        ("^1.*", (1, 0, 0)),
        ("^1.2", (1, 2, 0)),
        ("^1.2.*", (1, 2, 0)),
        ("^1.2.3", (1, 2, 3)),
        ("^1.2.3-alpha", (1, 2, 3)),
        ("^1.2.3-alpha+build", (1, 2, 3)),
        ("=1", (1, 0, 0)),
        ("=1.*", (1, 0, 0)),
        ("=1.2", (1, 2, 0)),
        ("=1.2.*", (1, 2, 0)),
        ("=1.2.3", (1, 2, 3)),
        ("=1.2.3-alpha", (1, 2, 3)),
        ("=1.2.3-alpha+build", (1, 2, 3)),
        ("~1", (1, 0, 0)),
        ("~1.*", (1, 0, 0)),
        ("~1.2", (1, 2, 0)),
        ("~1.2.*", (1, 2, 0)),
        ("~1.2.3", (1, 2, 3)),
        (">1", (2, 0, 0)),
        (">1.*", (2, 0, 0)),
        (">1.2", (1, 3, 0)),
        (">1.2.*", (1, 3, 0)),
        (">1.2.3", (1, 2, 4)),
        (">=1", (1, 0, 0)),
        (">=1.*", (1, 0, 0)),
        (">=1.2", (1, 2, 0)),
        (">=1.2.*", (1, 2, 0)),
        (">=1.2.3", (1, 2, 3)),
        ("<1", (0, 0, 0)),
        ("<1.*", (0, 0, 0)),
        ("<1.2", (0, 0, 0)),
        ("<1.2.*", (0, 0, 0)),
        ("<1.2.3", (0, 0, 0)),
        ("<=1", (0, 0, 0)),
        ("<=1.*", (0, 0, 0)),
        ("<=1.2", (0, 0, 0)),
        ("<=1.2.*", (0, 0, 0)),
        ("<=1.2.3", (0, 0, 0)),
    ],
)
def test_VersionSpec_min(pair):
    specification, expected = pair
    assert VersionSpec.parse(specification).min == Version(*expected)


@pytest.mark.parametrize(
    "pair",
    [
        ("*", None),
        ("1", (2, 0, 0)),
        ("1.*", (2, 0, 0)),
        ("1.2", (1, 3, 0)),
        ("1.2.*", (1, 3, 0)),
        ("1.2.3", (1, 2, 4)),
        ("^1", (2, 0, 0)),
        ("^1.*", (2, 0, 0)),
        ("^1.2", (1, 3, 0)),
        ("^1.2.*", (1, 3, 0)),
        ("^1.2.3", (1, 2, 4)),
        ("^1.2.3-alpha", (1, 2, 3, "alpha.1")),
        ("^1.2.3-alpha+build", (1, 2, 3, "alpha", "build.1")),
        ("=1", (1, 0, 1)),
        ("=1.*", (1, 0, 1)),
        ("=1.2", (1, 2, 1)),
        ("=1.2.*", (1, 2, 1)),
        ("=1.2.3", (1, 2, 4)),
        ("=1.2.3-alpha", (1, 2, 3, "alpha.1")),
        ("=1.2.3-alpha+build", (1, 2, 3, "alpha", "build.1")),
        ("~1", (2, 0, 0)),
        ("~1.*", (2, 0, 0)),
        ("~1.2", (1, 3, 0)),
        ("~1.2.*", (1, 3, 0)),
        ("~1.2.3", (1, 2, 4)),
        (">1", None),
        (">1.*", None),
        (">1.2", None),
        (">1.2.*", None),
        (">1.2.3", None),
        (">=1", None),
        (">=1.*", None),
        (">=1.2", None),
        (">=1.2.*", None),
        (">=1.2.3", None),
        ("<1", (1, 0, 0)),
        ("<1.*", (1, 0, 0)),
        ("<1.2", (1, 2, 0)),
        ("<1.2.*", (1, 2, 0)),
        ("<1.2.3", (1, 2, 3)),
        ("<=1", (2, 0, 0)),
        ("<=1.*", (2, 0, 0)),
        ("<=1.2", (1, 3, 0)),
        ("<=1.2.*", (1, 3, 0)),
        ("<=1.2.3", (1, 2, 4)),
    ],
)
def test_VersionSpec_max(pair):
    specification, expected = pair
    spec = VersionSpec.parse(specification)
    if expected is None:
        assert spec.max is None
    else:
        assert spec.max is not None
        assert spec.max == Version(*expected)


def test_specific():
    assert VersionSpec.parse("^1.2.3-alpha").max == Version(1, 2, 3, "alpha.1")
