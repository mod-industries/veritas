from attrs import define
from semver.version import Version

from veritas.exceptions import ParseError
from veritas.spec import VersionSpec


@define
class VersionRequirement:
    """Defines a set of version specifications that must be satisfied."""

    specs: list[VersionSpec]
    """List of defined version specifications."""

    def __str__(self) -> str:
        """String representation of the version requirement."""

        return ", ".join(str(spec) for spec in self.specs)

    @classmethod
    def parse(cls, requirement: str) -> "VersionRequirement":
        """
        Parse a version requirement string.

        Args:
            requirement (str): The version requirement string.

        Returns:
            VersionRequirement: The parsed version requirement.

        Raises:
            ParseError: If the given version requirement is invalid.
        """

        req = cls([VersionSpec.parse(spec.strip()) for spec in requirement.split(",")])
        req.validate()
        return req

    @property
    def constraints(self) -> tuple[Version, Version | None]:
        """Tuple of minimum and maximum versions imposed by the version requirement."""

        self.validate()
        return (
            max(spec.min for spec in self.specs),
            min(spec.max for spec in self.specs if spec.max is not None) or None,
        )

    def validate(self):
        """
        Validate that the version requirement does not include conflicting specifications.

        Raises:
            ValueError: If the version requirement includes conflicting specifications.
        """

        min_constraint = max(spec.min for spec in self.specs)
        max_constraint = min(spec.max for spec in self.specs if spec.max is not None)
        if min_constraint >= max_constraint:
            raise ParseError(
                "Minimum version (inclusive) is greater than maximum version (exclusive) "
                f'for requirement "{self!s}" (min: >={min_constraint}, max: <{max_constraint})'
            )
