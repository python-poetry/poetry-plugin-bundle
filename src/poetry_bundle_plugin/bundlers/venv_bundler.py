import subprocess
import sys

from subprocess import CalledProcessError
from typing import TYPE_CHECKING
from typing import Optional
from typing import Tuple
from typing import cast

from .bundler import Bundler


if TYPE_CHECKING:
    from pathlib import Path

    from cleo.io.io import IO
    from cleo.io.outputs.section_output import SectionOutput  # noqa
    from poetry.core.semver.version import Version
    from poetry.poetry import Poetry


class VenvBundler(Bundler):

    name: str = "venv"

    def __init__(self) -> None:
        self._path: Optional["Path"] = None
        self._executable: Optional[str] = None
        self._remove: bool = False

    def set_path(self, path: "Path") -> "VenvBundler":
        self._path = path

        return self

    def set_executable(self, executable: str) -> "VenvBundler":
        self._executable = executable

        return self

    def set_remove(self, remove: bool = True) -> "VenvBundler":
        self._remove = remove

        return self

    def bundle(self, poetry: "Poetry", io: "IO") -> bool:
        from pathlib import Path

        from cleo.io.null_io import NullIO
        from poetry.core.masonry.builders.wheel import WheelBuilder
        from poetry.core.masonry.utils.module import ModuleOrPackageNotFound
        from poetry.core.packages.package import Package
        from poetry.core.semver.version import Version
        from poetry.installation.installer import Installer
        from poetry.installation.operations.install import Install
        from poetry.utils.env import EnvManager
        from poetry.utils.env import SystemEnv
        from poetry.utils.env import VirtualEnv
        from poetry.utils.helpers import temporary_directory

        warnings = []

        manager = EnvManager(poetry)
        executable = self._executable
        if self._executable is not None:
            executable, python_version = self._get_executable_info(executable)
        else:
            version_info = SystemEnv(Path(sys.prefix)).get_version_info()
            python_version = Version.parse(".".join(str(v) for v in version_info[:3]))

        message = self._get_message(poetry, self._path)
        if io.is_decorated() and not io.is_debug():
            io = io.section()

        io.write_line(message)

        if self._path.exists():
            env = VirtualEnv(self._path)
            env_python_version = Version.parse(
                ".".join(str(v) for v in env.version_info[:3])
            )

            if (
                not env.is_sane()
                or env_python_version != python_version
                or self._remove
            ):
                self._write(
                    io, message + ": <info>Removing existing virtual environment</info>"
                )

                manager.remove_venv(str(self._path))

                self._write(
                    io,
                    message
                    + ": <info>Creating a virtual environment using Python <b>{}</b></info>".format(
                        python_version
                    ),
                )

                manager.build_venv(str(self._path), executable=executable)
            else:
                self._write(
                    io, message + ": <info>Using existing virtual environment</info>"
                )
        else:
            self._write(
                io,
                message
                + ": <info>Creating a virtual environment using Python <b>{}</b></info>".format(
                    python_version
                ),
            )

            manager.build_venv(str(self._path), executable=executable)

        env = VirtualEnv(self._path)

        self._write(
            io,
            message + ": <info>Installing dependencies</info>",
        )

        installer = Installer(
            NullIO() if not io.is_debug() else io,
            env,
            poetry.package,
            poetry.locker,
            poetry.pool,
            poetry.config,
        )
        installer.requires_synchronization()
        installer.use_executor(poetry.config.get("experimental.new-installer", False))

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
            message
            + ": <info>Installing <c1>{}</c1> (<b>{}</b>)</info>".format(
                poetry.package.pretty_name, poetry.package.pretty_version
            ),
        )

        # Build a wheel of the project in a temporary directory
        # and install it in the newly create virtual environment
        with temporary_directory() as directory:
            try:
                wheel_name = WheelBuilder.make_in(poetry, directory=Path(directory))
                wheel = Path(directory).joinpath(wheel_name)
                package = Package(
                    poetry.package.name,
                    poetry.package.version,
                    source_type="file",
                    source_url=wheel,
                )
                installer.executor.execute([Install(package)])
            except ModuleOrPackageNotFound:
                warnings.append(
                    "The root package was not installed because no matching module or package was found."
                )

        self._write(io, self._get_message(poetry, self._path, done=True))

        if warnings:
            for warning in warnings:
                io.write_line(
                    "  <fg=yellow;options=bold>•</> <warning>{}</warning>".format(
                        warning
                    )
                )

        return True

    def _get_message(
        self, poetry: "Poetry", path: "Path", done: bool = False, error: bool = False
    ) -> str:
        operation_color = "blue"

        if error:
            operation_color = "red"
        elif done:
            operation_color = "green"

        verb = "Bundling"
        if done:
            verb = "<success>Bundled</success>"

        return "  <fg={};options=bold>•</> {} <c1>{}</c1> (<b>{}</b>) into <c2>{}</c2>".format(
            operation_color,
            verb,
            poetry.package.pretty_name,
            poetry.package.pretty_version,
            path,
        )

    def _write(self, io: "IO", message: str) -> None:
        from cleo.io.outputs.section_output import SectionOutput  # noqa

        if io.is_debug() or not io.is_decorated() or not isinstance(io, SectionOutput):
            io.write_line(message)
            return

        io = cast(SectionOutput, io)
        io.overwrite(message)

    def _get_executable_info(self, executable: str) -> Tuple[str, "Version"]:
        from poetry.core.semver.version import Version
        from poetry.utils._compat import list_to_shell_command

        try:
            python_version = Version.parse(executable)
            executable = "python{}".format(python_version.major)
            if python_version.precision > 1:
                executable += ".{}".format(python_version.minor)
        except ValueError:
            # Executable in PATH or full executable path
            pass

        try:
            python_version = subprocess.check_output(
                list_to_shell_command(
                    [
                        executable,
                        "-c",
                        "\"import sys; print('.'.join([str(s) for s in sys.version_info[:3]]))\"",
                    ]
                ),
                shell=True,
            ).decode()
        except CalledProcessError as e:
            from poetry.utils.env import EnvCommandError

            raise EnvCommandError(e)

        python_version = Version.parse(python_version.strip())

        return executable, python_version
