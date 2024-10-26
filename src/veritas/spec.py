import re
from enum import Enum
from typing import Literal

from attrs import define, field
from semver import Version

from veritas.constants import VERSION_SPECIFICATION_PATTERN
from veritas.exceptions import ParseError

VersionSpecPart_T = int | Literal["*"] | None
"""
Defines the type of a version specification part.

A version specification part can be:
- An explicit integer value
- A wildcard (`*`)
- Not defined (`None`)
"""


class VersionOperation(Enum):
    """Enumeration of version operation types."""

    CARET = "^"
    """Any version compatible with at least the given value."""

    TILDE = "~"
    """Minimum version with restricted compatibility range."""

    EQ = "="
    """Exactly the specified version."""

    GT = ">"
    """Greater than the specified version."""

    GTE = ">="
    """Greater than or equal to the specified version."""

    LT = "<"
    """Less than the specified version."""

    LTE = "<="
    """Less than or equal to the specified version."""


@define
class VersionSpec:
    """Defines a single semantic version specification."""

    op: VersionOperation | None = field(default=None)
    """Operation applied to the version specification."""

    major: VersionSpecPart_T = field(default=None)
    """Major version specification."""

    minor: VersionSpecPart_T = field(default=None)
    """Minor version specification."""

    patch: VersionSpecPart_T = field(default=None)
    """Patch version specification."""

    prerelease: str | None = field(default=None)
    """Prerelease version specification."""

    build: str | None = field(default=None)
    """Build version specification."""

    def __str__(self) -> str:
        """String representation of the version specification."""

        version = f"{self.op.value}" if self.op is not None else ""
        version += f"{self.major if self.major != '*' else '*'}"
        version += f".{self.minor if self.minor != '*' else '*'}" if self.minor is not None else ""
        version += f".{self.patch if self.patch != '*' else '*'}" if self.patch is not None else ""
        version += f"-{self.prerelease}" if self.prerelease is not None else ""
        version += f"+{self.build}" if self.build is not None else ""
        return version

    @staticmethod
    def _parse_version_part(match: re.Match, group: str, wild_group: str) -> VersionSpecPart_T:
        """
        Parse a version part from a regular expression match.

        Args:
            match (re.Match): The regular expression match object.
            group (str): The name of the group to extract.
            wild_group (str): The name of the group that represents a wildcard.

        Returns:
            VersionSpecPart_T: The parsed version part.
        """

        return (
            int(match.group(group))
            if match.group(group)
            else "*"
            if match.group(wild_group)
            else None
        )

    @classmethod
    def parse(cls, specification: str) -> "VersionSpec":
        """
        Parse a version specification string.

        Args:
            specification (str): The version specification string.

        Returns:
            VersionSpec: The parsed version specification.

        Raises:
            ParseError: If the given version specification is invalid.
        """

        match = re.match(VERSION_SPECIFICATION_PATTERN, specification)
        if match is None:
            raise ParseError(f"Invalid version specification {specification!r}")

        return cls(
            op=VersionOperation(match.group("op")) if match.group("op") is not None else None,
            major=cls._parse_version_part(match, "major", "wild_major"),
            minor=cls._parse_version_part(match, "minor", "wild_minor"),
            patch=cls._parse_version_part(match, "patch", "wild_patch"),
            prerelease=match.group("prerelease"),
            build=match.group("build"),
        )

    def __base_version(self) -> Version:
        """Get the base version of the specification."""
        return Version(
            *(
                self.major if self.major and self.major != "*" else 0,
                self.minor if self.minor and self.minor != "*" else 0,
                self.patch if self.patch and self.patch != "*" else 0,
            )
        )

    @property
    def min(self) -> Version:
        """Minimum version (inclusive) that satisfies the specification."""

        if self.op in (VersionOperation.LT, VersionOperation.LTE):
            # When the version operation is LT or LTE, the minimum version the
            # lowest possible version
            return Version(0, 0, 0)

        version = self.__base_version()
        if self.op == VersionOperation.GT:
            # When the version operation is GT, the minimum version is the next greater version
            # for the first known version part
            if self.minor is None or self.minor == "*":
                return version.bump_major()
            elif self.patch is None or self.patch == "*":
                return version.bump_minor()
            else:
                return version.bump_patch()

        return version

    @property
    def max(self) -> Version | None:
        """Maximum version (exclusive) that satisfies the specification."""

        if self.op in (
            VersionOperation.GT,
            VersionOperation.GTE,
        ) or (self.major is None or self.major == "*"):
            # When the major version is a wildcard or the version operation is GT or GTE,
            # there is no maximum version
            return None

        version = self.__base_version()
        if self.op == VersionOperation.LT:
            # When the version operation is LT, the maximum version is the defined version
            return version
        elif self.op == VersionOperation.EQ:
            # When the version operation is EQ, the maximum version is next patch as we cannot
            # accept anything but the defined version exactly
            return version.bump_patch()
        elif self.op is None or self.op in (
            VersionOperation.CARET,
            VersionOperation.TILDE,
            VersionOperation.LTE,
        ):
            # When the version operation is not defined, or is CARET, TILDE, or LTE, the maximum
            # version is the next greater version for the first known part
            if self.minor is None or self.minor == "*":
                return version.bump_major()
            elif self.patch is None or self.patch == "*":
                return version.bump_minor()
            else:
                return version.bump_patch()

        return None  # pragma: no cover
