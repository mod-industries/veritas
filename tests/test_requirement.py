import pytest
from semver import Version

from veritas.exceptions import ParseError
from veritas.requirement import VersionRequirement


@pytest.mark.parametrize(
    "requirement",
    [
        "1",
        "1, <2",
        "1, <2, <3",
        ">1",
    ],
)
def test_VersionRequirement_parse(requirement: str):
    req = VersionRequirement.parse(requirement)
    assert str(req) == requirement


@pytest.mark.parametrize(
    "requirement",
    [
        "<1, >2",  # min > max
        "1, >1",  # 1 requires <2.0.0, >1 requires >=2.0.0
    ],
)
def test_VersionRequirement_parse_fails_on_invalid(requirement: str):
    with pytest.raises(ParseError):
        VersionRequirement.parse(requirement)


@pytest.mark.parametrize(
    "pair",
    [
        ("1, 1", ((1, 0, 0), (2, 0, 0))),
        ("1, ^1", ((1, 0, 0), (2, 0, 0))),
        ("1, =1", ((1, 0, 0), (1, 0, 1))),
        ("1, ~1", ((1, 0, 0), (2, 0, 0))),
        ("0.1, <1", ((0, 1, 0), (0, 2, 0))),
        ("1, <=1", ((1, 0, 0), (2, 0, 0))),
        ("1.2, <3", ((1, 2, 0), (1, 3, 0))),
        (">=1.2, <1.5", ((1, 2, 0), (1, 5, 0))),
    ],
)
def test_VersionRequirement_constraints(
    pair: tuple[str, tuple[tuple[int, int, int], tuple[int, int, int] | None]],
):
    requirement, (min_version, max_version) = pair
    (min_constraint, max_constraint) = VersionRequirement.parse(requirement).constraints
    assert min_constraint == Version(*min_version)
    if max_version is None:
        assert max_constraint is None
    else:
        assert max_constraint is not None
        assert max_constraint == Version(*max_version)


@pytest.mark.parametrize(
    "pair",
    [
        ("1", (0, 1, 0)),
        (">1", (1, 0, 0)),
    ],
)
def test_VersionRequirement_compare_lt(pair: tuple[str, tuple[int, int, int]]):
    requirement, version = pair
    assert VersionRequirement.parse(requirement).compare(Version(*version)) == -1


@pytest.mark.parametrize(
    "pair",
    [
        ("1", (2, 0, 0)),
        ("<1", (1, 0, 0)),
    ],
)
def test_VersionRequirement_compare_gt(pair: tuple[str, tuple[int, int, int]]):
    requirement, version = pair
    assert VersionRequirement.parse(requirement).compare(Version(*version)) == 1


@pytest.mark.parametrize(
    "pair",
    [
        ("1", (1, 0, 0)),
        (">=1", (1, 0, 0)),
    ],
)
def test_VersionREquirement_compare_eq(pair: tuple[str, tuple[int, int, int]]):
    requirement, version = pair
    assert VersionRequirement.parse(requirement).compare(Version(*version)) == 0


@pytest.mark.parametrize(
    "pair",
    [
        ("1, 1", (1, 0, 0)),
        ("1, <2", (1, 0, 0)),
        ("1, <2, <3", (1, 0, 0)),
        (">1", (2, 0, 0)),
    ],
)
def test_VersionRequirement_check(pair: tuple[str, tuple[int, int, int]]):
    requirement, version = pair
    assert VersionRequirement.parse(requirement).check(Version(*version))
