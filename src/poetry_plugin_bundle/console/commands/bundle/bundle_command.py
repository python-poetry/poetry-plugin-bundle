from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.console.commands.group_command import GroupCommand


if TYPE_CHECKING:
    from poetry_plugin_bundle.bundlers.bundler import Bundler
    from poetry_plugin_bundle.bundlers.bundler_manager import BundlerManager


class BundleCommand(GroupCommand):
    """
    Base class for all bundle commands.
    """

    bundler_name: str

    def __init__(self) -> None:
        self._bundler_manager: BundlerManager | None = None

        super().__init__()

    @property
    def bundler_manager(self) -> BundlerManager | None:
        return self._bundler_manager

    def set_bundler_manager(self, bundler_manager: BundlerManager) -> None:
        self._bundler_manager = bundler_manager

    def configure_bundler(self, bundler: Bundler) -> None:
        """
        Configure the given bundler based on command specific options and arguments.
        """
        pass

    def handle(self) -> int:
        self.line("")

        assert self._bundler_manager is not None
        bundler = self._bundler_manager.bundler(self.bundler_name)

        self.configure_bundler(bundler)

        return int(not bundler.bundle(self.poetry, self._io))
