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
        from poetry.core.masonry.utils.module import ModuleOrPackageNotFoundError
        from poetry.core.packages.package import Package
        from poetry.installation.installer import Installer
        from poetry.installation.operations.install import Install
        from poetry.packages.locker import Locker
        from poetry.utils.env import EnvManager
        from poetry.utils.env.python import Python
        from poetry.utils.env.python.exceptions import InvalidCurrentPythonVersionError

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
                self,
                path: Path,
                python: Python | None,
                force: bool,
            ) -> Env:
                self._path = path
                return self.create_venv(name=None, python=python, force=force)

        warnings = []

        manager = CustomEnvManager(poetry)
        executable = Path(self._executable) if self._executable else None
        python = Python(executable) if executable else None

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
                self._path, python=python, force=self._remove
            )
        except InvalidCurrentPythonVersionError:
            self._write(
                io,
                f"{message}: <info>Replacing existing virtual environment"
                " due to incompatible Python version</info>",
            )
            env = manager.create_venv_at_path(self._path, python=python, force=True)

        if self._platform:
            self._constrain_env_platform(env, self._platform)

        self._write(io, f"{message}: <info>Installing dependencies</info>")

        class CustomLocker(Locker):
            def locked_repository(self) -> LockfileRepository:
                repo = super().locked_repository()
                for package in repo.packages:
                    package.develop = False
                return repo

        custom_locker = CustomLocker(poetry.locker.lock, poetry.locker._pyproject_data)

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

        # Skip building the wheel if is_package_mode exists and is set to false
        if hasattr(poetry, "is_package_mode") and not poetry.is_package_mode:
            self._write(
                io,
                f"{message}: <info>Skipping installation for non package project"
                f" <c1>{poetry.package.pretty_name}</c1>",
            )
        else:
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
                except ModuleOrPackageNotFoundError:
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

    def _constrain_env_platform(self, env: Env, platform: str) -> None:
        """
        Set the argument environment's supported tags
        based on the configured platform override.
        """
        from poetry_plugin_bundle.utils.platforms import create_supported_tags

        env._supported_tags = create_supported_tags(platform, env)
