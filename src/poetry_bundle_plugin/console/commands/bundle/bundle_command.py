from typing import TYPE_CHECKING
from typing import Optional

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from poetry_bundle_plugin.bundlers.bundler import Bundler
    from poetry_bundle_plugin.bundlers.bundler_manager import BundlerManager


class BundleCommand(Command):
    """
    Base class for all bundle commands.
    """

    bundler_name: Optional[str] = None

    def __init__(self) -> None:
        self._bundler_manager: Optional["BundlerManager"] = None

        super().__init__()

    @property
    def bundler_manager(self) -> "BundlerManager":
        return self._bundler_manager

    def set_bundler_manager(self, bundler_manager: "BundlerManager") -> None:
        self._bundler_manager = bundler_manager

    def configure_bundler(self, bundler: "Bundler") -> None:
        """
        Configure the given bundler based on command specific options and arguments.
        """
        pass

    def handle(self) -> int:
        self.line("")

        bundler = self._bundler_manager.bundler(self.bundler_name)

        self.configure_bundler(bundler)

        return int(not bundler.bundle(self.poetry, self._io))
