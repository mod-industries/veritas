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
        """Tuple of minimum (inclusive) and maximum (exclusive) versions imposed by the requirement."""

        self.validate()

        spec_max_constraints = [spec.max for spec in self.specs if spec.max is not None]
        return (
            max(spec.min for spec in self.specs),
            min(spec_max_constraints) if len(spec_max_constraints) > 0 else None,
        )

    def validate(self):
        """
        Validate that the version requirement does not include conflicting specifications.

        Raises:
            ValueError: If the version requirement includes conflicting specifications.
        """

        min_constraint = max(spec.min for spec in self.specs)
        spec_max_constraints = [spec.max for spec in self.specs if spec.max is not None]
        max_constraint = min(spec_max_constraints) if len(spec_max_constraints) > 0 else None

        if max_constraint is not None and min_constraint >= max_constraint:
            raise ParseError(
                "Minimum version (inclusive) is greater than maximum version (exclusive) "
                f'for requirement "{self!s}" (min: >={min_constraint}, max: <{max_constraint})'
            )

    def compare(self, version: Version) -> int:
        """
        Compare the given version to the version requirement.

        Args:
            version (Version): The version to compare.

        Returns:
            int: -1 if the version is less than the requirement, 0 if equal, 1 if greater.
        """

        min_constraint, max_constraint = self.constraints
        if version < min_constraint:
            return -1

        # The max constraint is exclusive, so we also need to check if the version is equal to it
        if max_constraint is not None and version >= max_constraint:
            return 1

        return 0

    def check(self, version: Version) -> bool:
        """
        Check if the given version satisfies the version requirement.

        Args:
            version (Version): The version to check.

        Returns:
            bool: `True` if the version satisfies the requirement, `False` otherwise.
        """

        return self.compare(version) == 0
