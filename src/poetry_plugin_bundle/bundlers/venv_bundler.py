from __future__ import annotations

from typing import TYPE_CHECKING

from poetry_plugin_bundle.bundlers.bundler import Bundler


if TYPE_CHECKING:
    from pathlib import Path

    from cleo.io.io import IO
    from cleo.io.outputs.section_output import SectionOutput
    from poetry.poetry import Poetry
    from poetry.repositories.lockfile_repository import LockfileRepository
    from poetry.utils.env import Env


class VenvBundler(Bundler):
    name = "venv"

    def __init__(self) -> None:
        self._path: Path
        self._executable: str | None = None
        self._remove: bool = False
        self._activated_groups: set[str] | None = None
        self._compile: bool = False
        self._platform: str | None = None

    def set_path(self, path: Path) -> VenvBundler:
        self._path = path

        return self

    def set_executable(self, executable: str | None) -> VenvBundler:
        self._executable = executable

        return self

    def set_activated_groups(self, activated_groups: set[str]) -> VenvBundler:
        self._activated_groups = activated_groups

        return self

    def set_remove(self, remove: bool = True) -> VenvBundler:
        self._remove = remove

        return self

    def set_compile(self, compile: bool = False) -> VenvBundler:
        self._compile = compile

        return self

    def set_platform(self, platform: str | None) -> VenvBundler:
        self._platform = platform

        return self

    def bundle(self, poetry: Poetry, io: IO) -> bool:
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from cleo.io.null_io import NullIO
        from poetry.core.masonry.builders.wheel import WheelBuilder
        from poetry.core.masonry.utils.module import ModuleOrPackageNotFound
        from poetry.core.packages.package import Package
        from poetry.installation.installer import Installer
        from poetry.installation.operations.install import Install
        from poetry.packages.locker import Locker
        from poetry.utils.env import EnvManager
        from poetry.utils.env import InvalidCurrentPythonVersionError

        class CustomEnvManager(EnvManager):
            """
            This class is used as an adapter for allowing us to use
            Poetry's EnvManager.create_venv but with a custom path.
            It works by hijacking the "in_project_venv" concept so that
            we can get that behavior, but with a custom path.
            """

            @property
            def in_project_venv(self) -> Path:
                return self._path

            def use_in_project_venv(self) -> bool:
                return True

            def in_project_venv_exists(self) -> bool:
                """
                Coerce this call to always return True so that we avoid the path in the base
                EnvManager.get that detects an existing env residing at the centralized Poetry
                virtualenvs_path location.
                """
                return True

            def create_venv_at_path(
                self, path: Path, executable: Path | None, force: bool
            ) -> Env:
                self._path = path
                return self.create_venv(name=None, executable=executable, force=force)

        warnings = []

        manager = CustomEnvManager(poetry)
        executable = Path(self._executable) if self._executable else None

        message = self._get_message(poetry, self._path)
        if io.is_decorated() and not io.is_debug():
            io = io.section()  # type: ignore[assignment]

        io.write_line(message)

        if executable:
            self._write(
                io,
                f"{message}: <info>Creating a virtual environment using Python"
                f" <b>{executable}</b></info>",
            )
        else:
            self._write(
                io,
                f"{message}: <info>Creating a virtual environment"
                " using Poetry-determined Python",
            )

        try:
            env = manager.create_venv_at_path(
                self._path, executable=executable, force=self._remove
            )
        except InvalidCurrentPythonVersionError:
            self._write(
                io,
                f"{message}: <info>Replacing existing virtual environment"
                " due to incompatible Python version</info>",
            )
            env = manager.create_venv_at_path(
                self._path, executable=executable, force=True
            )

        if self._platform:
            self.constrain_env_platform(env)

        self._write(io, f"{message}: <info>Installing dependencies</info>")

        class CustomLocker(Locker):
            def locked_repository(self) -> LockfileRepository:
                repo = super().locked_repository()
                for package in repo.packages:
                    package.develop = False
                return repo

        custom_locker = CustomLocker(poetry.locker.lock, poetry.local_config)

        installer = Installer(
            NullIO() if not io.is_debug() else io,
            env,
            poetry.package,
            custom_locker,
            poetry.pool,
            poetry.config,
        )
        if self._activated_groups is not None:
            installer.only_groups(self._activated_groups)
        installer.requires_synchronization()

        installer.executor.enable_bytecode_compilation(self._compile)

        return_code = installer.run()
        if return_code:
            self._write(
                io,
                self._get_message(poetry, self._path, error=True)
                + ": <error>Failed</> at step <b>Installing dependencies</b>",
            )
            return False

        self._write(
            io,
            f"{message}: <info>Installing <c1>{poetry.package.pretty_name}</c1>"
            f" (<b>{poetry.package.pretty_version}</b>)</info>",
        )

        # Build a wheel of the project in a temporary directory
        # and install it in the newly create virtual environment
        with TemporaryDirectory() as directory:
            try:
                wheel_name = WheelBuilder.make_in(poetry, directory=Path(directory))
                wheel = Path(directory).joinpath(wheel_name)
                package = Package(
                    poetry.package.name,
                    poetry.package.version,
                    source_type="file",
                    source_url=str(wheel),
                )
                installer.executor.execute([Install(package)])
            except ModuleOrPackageNotFound:
                warnings.append(
                    "The root package was not installed because no matching module or"
                    " package was found."
                )

        self._write(io, self._get_message(poetry, self._path, done=True))

        if warnings:
            for warning in warnings:
                io.write_line(
                    f"  <fg=yellow;options=bold>•</> <warning>{warning}</warning>"
                )

        return True

    def _get_message(
        self, poetry: Poetry, path: Path, done: bool = False, error: bool = False
    ) -> str:
        operation_color = "blue"

        if error:
            operation_color = "red"
        elif done:
            operation_color = "green"

        verb = "Bundling"
        if done:
            verb = "<success>Bundled</success>"

        return (
            f"  <fg={operation_color};options=bold>•</>"
            f" {verb} <c1>{poetry.package.pretty_name}</c1>"
            f" (<b>{poetry.package.pretty_version}</b>) into <c2>{path}</c2>"
        )

    def _write(self, io: IO | SectionOutput, message: str) -> None:
        from cleo.io.outputs.section_output import SectionOutput

        if io.is_debug() or not io.is_decorated() or not isinstance(io, SectionOutput):
            io.write_line(message)
            return

        io.overwrite(message)

    def constrain_env_platform(self, env: Env) -> None:
        """
        TODO BW DOCME
        This isn't quite achieving what I want.  It is causing earlier but compatible platforms to be discarded.
        I need to be able to somehow generate all of the earlier compatible platforms starting from the specified
        platform.
        The key is in .venv/lib/python3.11/site-packages/packaging/tags.py
        It starts with sys_tags()
        Is there a way I can query for compatibility?

        yield from _manylinux.platform_tags(archs)

        Idea: Use the poetry.lock file to build a list of all the tags and then filter down
              based on the argument platform.  Nah, that will break with the manylinux value wonkiness.

        See src/pip/_internal/utils/compatibility_tags.py
            _custom_manylinux_platforms
            _expand_allowed_platforms

        Wait, how does Poetry parse the wheel filenames to determine if it is compatible?
        These involve ambiguous underscore values like "manylinux_2_28_x86_64"
        Check out the poetry Wheel class.  it might be helpful.
        """

        # TODO BW: Dynamically generate the interpreter and max python version.
        env._supported_tags = create_supported_tags(platform=self._platform, interpreter="cp39", max_python_version=(3,9))

if TYPE_CHECKING:
    from packaging.tags import Tag


def create_supported_tags(platform: str, interpreter: str, max_python_version: tuple[int]) -> list[Tag]:
    """
    """
    from packaging.tags import cpython_tags, compatible_tags

    if platform.startswith("manylinux"):
        supported_platforms = create_supported_manylinux_platforms(platform)
    elif platform.startswith("musllinux"):
        raise NotImplementedError(f"Platform {platform} not supported")
    elif platform.startswith("macosx"):
        supported_platforms = create_supported_macosx_platforms(platform)
    else:
        raise NotImplementedError(f"Platform {platform} not supported")

    tags = list(cpython_tags(python_version=max_python_version, platforms=supported_platforms))

    tags.extend(compatible_tags(interpreter=interpreter, python_version=max_python_version, platforms=supported_platforms))

    return tags


def create_supported_manylinux_platforms(platform: str) -> list[str]:
    """
    https://peps.python.org/pep-0600/
    manylinux_${GLIBCMAJOR}_${GLIBCMINOR}_${ARCH}

    For now, only GLIBCMAJOR "2" is supported.  It is unclear if there will be a need to support a future major
    version like "3" and if specified, how generate the compatible 2.x version tags.
    """
    import re

    # Implementation based on https://peps.python.org/pep-0600/#package-installers

    tag = normalize_legacy_manylinux_alias(platform)
    match = re.match("manylinux_([0-9]+)_([0-9]+)_(.*)", tag)
    if not match:
        raise ValueError(f"Invalid manylinux tag: {tag}")
    tag_major_str, tag_minor_str, tag_arch = match.groups()
    tag_major_max = int(tag_major_str)
    tag_minor_max = int(tag_minor_str)

    return [
        f"manylinux_{tag_major_max}_{tag_minor}_{tag_arch}"
        for tag_minor in range(tag_minor_max, -1, -1)
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

    return list(mac_platforms(version=(tag_major_max,tag_minor_max), arch=tag_arch))