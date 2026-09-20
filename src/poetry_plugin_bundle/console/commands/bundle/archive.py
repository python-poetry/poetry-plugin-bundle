from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cleo.helpers import argument
from cleo.helpers import option

from poetry_plugin_bundle.console.commands.bundle.bundle_command import BundleCommand


if TYPE_CHECKING:
    from poetry_plugin_bundle.bundlers.archive_bundler import ArchiveBundler


class BundleArchiveCommand(BundleCommand):
    name = "bundle archive"
    description = "Bundle the current project into an archive (.zip, .tar)"

    arguments = [argument("path", "Path to save archive in")]  # noqa: RUF012

    options = [  # noqa: RUF012
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
        option(
            "format",
            "f",
            "Archive format as supported by shutil.make_archive",
            flag=False,
            default="zip",
        ),
        option(
            "site-packages-only",
            None,
            "Only archive the Lib/site-packages directory",
            flag=True,
        ),
    ]

    bundler_name = "archive"

    def configure_bundler(
        self, bundler: ArchiveBundler  # type: ignore[override]
    ) -> None:
        bundler.set_path(Path(self.argument("path")))
        bundler.set_executable(self.option("python"))
        bundler.set_remove(self.option("clear"))
        bundler.set_activated_groups(self.activated_groups)

        bundler.set_format(self.option("format"))
        bundler.set_site_packages_only(self.option("site-packages-only"))
