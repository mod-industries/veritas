SEMVER_PATTERN = (
    r"\A(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?\Z"
)
"""Regular expression for semantic versioning."""

VERSION_SPECIFICATION_PATTERN = (
    r"\A(?:(?P<op>[=~^><]|[><]=)?"
    r"(?P<major>0|[1-9]\d*)"
    r"(?:\.(?P<minor>0|[1-9]\d*)"
    r"(?:\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)"
    r"|\-(?P<wild_prerelease>\*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)"
    r"|\+(?P<wild_build>\*))?"
    r"|\.(?P<wild_patch>\*))?"
    r"|\.(?P<wild_minor>\*))?"
    r"|(?P<wild_major>\*))\Z"
)
"""Regular expression for version specifications."""
