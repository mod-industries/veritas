"""Semver-based version specifications and requirement parsing."""

from veritas.requirement import VersionRequirement
from veritas.spec import Version, VersionOperation, VersionSpec

__all__ = ["VersionRequirement", "VersionOperation", "VersionSpec", "Version"]
