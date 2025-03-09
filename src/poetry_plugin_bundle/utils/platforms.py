from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from packaging.tags import Tag
    from poetry.utils.env import Env


@dataclass
class PlatformTagParseResult:
    platform: str
    version_major: int
    version_minor: int
    arch: str

    @staticmethod
    def parse(tag: str) -> PlatformTagParseResult:
        import re

        match = re.match("([a-z]+)_([0-9]+)_([0-9]+)_(.*)", tag)
        if not match:
            raise ValueError(f"Invalid platform tag: {tag}")
        platform, version_major_str, version_minor_str, arch = match.groups()
        return PlatformTagParseResult(
            platform=platform,
            version_major=int(version_major_str),
            version_minor=int(version_minor_str),
            arch=arch,
        )

    def to_tag(self) -> str:
        return "_".join(
            [self.platform, str(self.version_major), str(self.version_minor), self.arch]
        )


def create_supported_tags(platform: str, env: Env) -> list[Tag]:
    """
    Given a platform specifier string, generate a list of compatible tags
    for the argument environment's interpreter.

    Refer to:
        https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#platform-tag
        https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-platform
    """
    from packaging.tags import INTERPRETER_SHORT_NAMES
    from packaging.tags import compatible_tags
    from packaging.tags import cpython_tags
    from packaging.tags import generic_tags

    if platform.startswith("manylinux"):
        supported_platforms = create_supported_manylinux_platforms(platform)
    elif platform.startswith("musllinux"):
        supported_platforms = create_supported_musllinux_platforms(platform)
    elif platform.startswith("macosx"):
        supported_platforms = create_supported_macosx_platforms(platform)
    else:
        raise NotImplementedError(f"Platform {platform} not supported")

    python_implementation = env.python_implementation.lower()
    python_version = env.version_info[:2]
    interpreter_name = INTERPRETER_SHORT_NAMES.get(
        python_implementation, python_implementation
    )
    interpreter = None

    if interpreter_name == "cp":
        tags = list(
            cpython_tags(python_version=python_version, platforms=supported_platforms)
        )
        interpreter = f"{interpreter_name}{python_version[0]}{python_version[1]}"
    else:
        tags = list(
            generic_tags(
                interpreter=interpreter, abis=[], platforms=supported_platforms
            )
        )

    tags.extend(
        compatible_tags(
            interpreter=interpreter,
            python_version=python_version,
            platforms=supported_platforms,
        )
    )

    return tags


def create_supported_manylinux_platforms(platform: str) -> list[str]:
    """
    https://peps.python.org/pep-0600/
    manylinux_${GLIBCMAJOR}_${GLIBCMINOR}_${ARCH}

    For now, only GLIBCMAJOR "2" is supported.  It is unclear if there will be a need to support a future major
    version like "3" and if specified, how generate the compatible 2.x version tags.
    """
    # Implementation based on https://peps.python.org/pep-0600/#package-installers

    tag = normalize_legacy_manylinux_alias(platform)

    parsed = PlatformTagParseResult.parse(tag)
    return [
        f"{parsed.platform}_{parsed.version_major}_{tag_minor}_{parsed.arch}"
        for tag_minor in range(parsed.version_minor, -1, -1)
    ]


LEGACY_MANYLINUX_ALIASES = {
    "manylinux1": "manylinux_2_5",
    "manylinux2010": "manylinux_2_12",
    "manylinux2014": "manylinux_2_17",
}


def normalize_legacy_manylinux_alias(tag: str) -> str:
    tag_os_index_end = tag.index("_")
    tag_os = tag[:tag_os_index_end]
    tag_arch_suffix = tag[tag_os_index_end:]
    os_replacement = LEGACY_MANYLINUX_ALIASES.get(tag_os)
    if not os_replacement:
        return tag

    return os_replacement + tag_arch_suffix


def create_supported_macosx_platforms(platform: str) -> list[str]:
    import re

    from packaging.tags import mac_platforms

    match = re.match("macosx_([0-9]+)_([0-9]+)_(.*)", platform)
    if not match:
        raise ValueError(f"Invalid macosx tag: {platform}")
    tag_major_str, tag_minor_str, tag_arch = match.groups()
    tag_major_max = int(tag_major_str)
    tag_minor_max = int(tag_minor_str)

    return list(mac_platforms(version=(tag_major_max, tag_minor_max), arch=tag_arch))


def create_supported_musllinux_platforms(platform: str) -> list[str]:
    import re

    match = re.match("musllinux_([0-9]+)_([0-9]+)_(.*)", platform)
    if not match:
        raise ValueError(f"Invalid musllinux tag: {platform}")
    tag_major_str, tag_minor_str, tag_arch = match.groups()
    tag_major_max = int(tag_major_str)
    tag_minor_max = int(tag_minor_str)

    return [
        f"musllinux_{tag_major_max}_{minor}_{tag_arch}"
        for minor in range(tag_minor_max, -1, -1)
    ]
