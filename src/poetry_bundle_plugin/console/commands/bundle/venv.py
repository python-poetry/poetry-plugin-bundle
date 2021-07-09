from pathlib import Path
from typing import TYPE_CHECKING

from cleo.helpers import argument
from cleo.helpers import option

from .bundle_command import BundleCommand


if TYPE_CHECKING:
    from poetry_bundle_plugin.bundlers.venv_bundler import VenvBundler  # noqa


class BundleVenvCommand(BundleCommand):

    name = "bundle venv"
    description = "Bundle the current project into a virtual environment"

    arguments = [
        argument("path", "The path to the virtual environment to bundle into."),
    ]

    options = [
        option(
            "python",
            "p",
            "The Python executable to use to create the virtual environment. "
            "Defaults to the current Python executable",
            flag=False,
            value_required=True,
        ),
        option(
            "clear",
            None,
            "Clear the existing virtual environment if it exists. ",
            flag=True,
        ),
    ]

    bundler_name = "venv"

    def configure_bundler(self, bundler: "VenvBundler") -> None:
        bundler.set_path(Path(self.argument("path")))
        bundler.set_executable(self.option("python"))
        bundler.set_remove(self.option("clear"))
