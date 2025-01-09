from __future__ import annotations

import pytest

from poetry.utils.env import MockEnv

import poetry_plugin_bundle.utils.platforms as platforms


def _get_supported_tags_set(
    platform: str, python_version_info: tuple[int, int, int]
) -> set[str]:
    env = MockEnv(version_info=python_version_info)
    result = platforms.create_supported_tags(platform, env)
    return {str(tag) for tag in result}


def _test_create_supported_tags(
    platform: str,
    python_version_info: tuple[int, int, int],
    expected_tags: set[str],
    unexpected_tags: set[str],
) -> None:
    result_set = _get_supported_tags_set(platform, python_version_info)

    assert result_set.issuperset(expected_tags)
    assert not result_set.intersection(unexpected_tags)


def test_create_supported_tags_manylinux() -> None:
    _test_create_supported_tags(
        platform="manylinux_2_12_x86_64",
        python_version_info=(3, 12, 1),
        expected_tags={
            "cp312-cp312-manylinux_2_12_x86_64",
            "cp312-none-manylinux_2_12_x86_64",
            "cp312-abi3-manylinux_2_12_x86_64",
            "cp312-cp312-manylinux_2_1_x86_64",
            "cp311-abi3-manylinux_2_12_x86_64",
            "py312-none-manylinux_2_12_x86_64",
            "py312-none-any",
            "cp312-none-any",
        },
        unexpected_tags={
            "cp313-cp313-manylinux_2_12_x86_64",
            "cp312-cp312-manylinux_2_13_x86_64",
        },
    )


def test_create_supported_tags_legacy_manylinux_aliases() -> None:
    _test_create_supported_tags(
        platform="manylinux1_x86_64",
        python_version_info=(3, 10, 2),
        expected_tags={
            "cp310-cp310-manylinux_2_5_x86_64",
            "cp310-cp310-manylinux_2_1_x86_64",
        },
        unexpected_tags={
            "cp310-cp310-manylinux_2_6_x86_64",
        },
    )

    _test_create_supported_tags(
        platform="manylinux2010_x86_64",
        python_version_info=(3, 10, 2),
        expected_tags={
            "cp310-cp310-manylinux_2_12_x86_64",
            "cp310-cp310-manylinux_2_1_x86_64",
        },
        unexpected_tags={
            "cp310-cp310-manylinux_2_13_x86_64",
        },
    )

    _test_create_supported_tags(
        platform="manylinux2014_x86_64",
        python_version_info=(3, 11, 9),
        expected_tags={
            "cp311-cp311-manylinux_2_17_x86_64",
            "cp311-cp311-manylinux_2_1_x86_64",
        },
        unexpected_tags={
            "cp311-cp311-manylinux_2_24_x86_64",
        },
    )


def test_create_supported_tags_macosx() -> None:
    _test_create_supported_tags(
        platform="macosx_11_0_arm64",
        python_version_info=(3, 11, 8),
        expected_tags={
            "cp311-abi3-macosx_11_0_arm64",
            "cp311-abi3-macosx_10_12_universal2",
            "cp311-none-macosx_11_0_universal2",
            "py311-none-any",
        },
        unexpected_tags={
            "cp311-none-macosx_11_1_universal2",
        },
    )

    _test_create_supported_tags(
        platform="macosx_10_9_x86_64",
        python_version_info=(3, 11, 8),
        expected_tags={
            "cp311-abi3-macosx_10_9_universal2",
            "cp311-abi3-macosx_10_9_x86_64",
            "cp311-abi3-macosx_10_9_intel",
            "cp311-none-macosx_10_7_universal2",
            "py311-none-any",
        },
        unexpected_tags={
            "cp311-none-macosx_11_1_universal2",
            "cp311-abi3-macosx_11_0_arm64",
        },
    )


def test_create_supported_tags_musllinux() -> None:
    _test_create_supported_tags(
        platform="musllinux_1_1_x86_64",
        python_version_info=(3, 13, 1),
        expected_tags={
            "cp313-cp313-musllinux_1_1_x86_64",
            "cp313-abi3-musllinux_1_1_x86_64",
            "py312-none-any",
            "cp313-none-any",
        },
        unexpected_tags={
            "cp313-cp313-musllinux_1_2_x86_64",
        },
    )


def test_create_supported_tags_unsupported_platform() -> None:
    env = MockEnv(version_info=(3, 12, 1))

    unsupported_platforms = [
        "win32",
        "linux",
        "foobar",
    ]
    for platform in unsupported_platforms:
        with pytest.raises(NotImplementedError):
            platforms.create_supported_tags(platform, env)


def test_create_supported_tags_malformed_platforms() -> None:
    env = MockEnv(version_info=(3, 12, 1))

    malformed_platforms = [
        "macosx_11_blah_arm64",
        "macosx",
        "manylinux_blammo_12_x86_64",
        "manylinux_x86_64",
        "manylinux",
        "musllinux_?_1_x86_64",
        "musllinux",
    ]
    for platform in malformed_platforms:
        with pytest.raises(ValueError):
            platforms.create_supported_tags(platform, env)
