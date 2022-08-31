from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cleo.helpers import argument
from cleo.helpers import option

from poetry_plugin_bundle.console.commands.bundle.bundle_command import BundleCommand


if TYPE_CHECKING:
    from poetry_plugin_bundle.bundlers.venv_bundler import VenvBundler


class BundleVenvCommand(BundleCommand):
    name = "bundle venv"
    description = "Bundle the current project into a virtual environment"

    arguments = [
        argument("path", "The path to the virtual environment to bundle into.")
    ]

    options = [
        *BundleCommand._group_dependency_options(),
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

    def configure_bundler(self, bundler: VenvBundler) -> None:  # type: ignore[override]
        bundler.set_path(Path(self.argument("path")))
        bundler.set_executable(self.option("python"))
        bundler.set_remove(self.option("clear"))
        bundler.set_activated_groups(self.activated_groups)
