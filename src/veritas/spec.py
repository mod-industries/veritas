import re
from enum import Enum
from typing import Literal

from attrs import define, field
from semver import Version

from veritas.constants import VERSION_SPECIFICATION_PATTERN

WILD: Literal["*"] = "*"
"""Wildcard character for version specification parts."""


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


@define(hash=True)
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

        parts: list[str] = []
        if self.op is not None:
            parts.append(self.op.value)

        parts.append(str(self.major if self.major != WILD else WILD))
        if self.minor is not None:
            parts.append(f".{self.minor if self.minor != WILD else WILD}")
        if self.patch is not None:
            parts.append(f".{self.patch if self.patch != WILD else WILD}")
        if self.prerelease is not None:
            parts.append(f"-{self.prerelease if self.prerelease != WILD else WILD}")
        if self.build is not None:
            parts.append(f"+{self.build if self.build != WILD else WILD}")

        return "".join(parts)

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

        part = match.group(group)
        if part is not None:
            return int(part)
        elif match.group(wild_group) is not None:
            return WILD

        return None

    @staticmethod
    def _parse_version_str(match: re.Match, group: str, wild_group: str) -> str | None:
        """
        Parse a version string from a regular expression match.

        Args:
            match (re.Match): The regular expression match object.
            group (str): The name of the group to extract.
            wild_group (str): The name of the group that represents a wildcard.

        Returns:
            str | None: The parsed version string.
        """

        version = match.group(group)
        if version is not None:
            return version
        elif match.group(wild_group) is not None:
            return WILD

        return None

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
            raise ValueError(f"Invalid version specification {specification!r}")

        return cls(
            op=VersionOperation(match.group("op")) if match.group("op") is not None else None,
            major=cls._parse_version_part(match, "major", "wild_major"),
            minor=cls._parse_version_part(match, "minor", "wild_minor"),
            patch=cls._parse_version_part(match, "patch", "wild_patch"),
            prerelease=cls._parse_version_str(match, "prerelease", "wild_prerelease"),
            build=cls._parse_version_str(match, "build", "wild_build"),
        )

    def __base_version(self) -> Version:
        """Get the base version of the specification."""
        return Version(
            major=self.major if self.major and self.major != WILD else 0,
            minor=self.minor if self.minor and self.minor != WILD else 0,
            patch=self.patch if self.patch and self.patch != WILD else 0,
            prerelease=self.prerelease if self.prerelease and self.prerelease != WILD else None,
            build=self.build if self.build and self.build != WILD else None,
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
            if self.minor is None or self.minor == WILD:
                return version.bump_major()
            elif self.patch is None or self.patch == WILD:
                return version.bump_minor()
            elif self.prerelease is None or self.prerelease == WILD:
                return version.bump_patch()
            elif self.build is None or self.build == WILD:
                return version.replace(prerelease=None).bump_prerelease(self.prerelease)
            else:
                return version.replace(build=None).bump_build(self.build)

        return version

    @property
    def max(self) -> Version | None:
        """Maximum version (exclusive) that satisfies the specification."""

        if self.op in (
            VersionOperation.GT,
            VersionOperation.GTE,
        ) or (self.major is None or self.major == WILD):
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
            if self.build is not None and self.build != WILD:
                return version.replace(build=None).bump_build(self.build)
            elif self.prerelease is not None and self.prerelease != WILD:
                return version.replace(prerelease=None).bump_prerelease(self.prerelease)

            return version.bump_patch()
        elif self.op is None or self.op in (
            VersionOperation.CARET,
            VersionOperation.TILDE,
            VersionOperation.LTE,
        ):
            # When the version operation is not defined, or is CARET, TILDE, or LTE, the maximum
            # version is the next greater version for the first known part
            if self.minor is None or self.minor == WILD:
                return version.bump_major()
            elif self.patch is None or self.patch == WILD:
                return version.bump_minor()
            elif self.prerelease is None or self.prerelease == WILD:
                return version.bump_patch()
            elif self.build is None or self.build == WILD:
                return version.replace(prerelease=None).bump_prerelease(self.prerelease)
            else:
                return version.replace(build=None).bump_build(self.build)

        return None  # pragma: no cover

    def compare(self, version: Version) -> int:
        """
        Compare the version with the specification.

        Args:
            version (Version): The version to compare.

        Returns:
            int: -1 if the version is less than the specification, 0 if equal, 1 if greater.
        """

        if self.min > version:
            return -1

        if self.max is not None and version >= self.max:
            return 1

        return 0

    def check(self, version: Version) -> bool:
        """
        Check if the version satisfies the specification.

        Args:
            version (Version): The version to check.

        Returns:
            bool: `True` if the version satisfies the specification, `False` otherwise.
        """

        return self.compare(version) == 0
