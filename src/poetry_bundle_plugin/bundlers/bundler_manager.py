from typing import TYPE_CHECKING
from typing import Dict
from typing import Type

from poetry_bundle_plugin.exceptions import BundlerManagerError


if TYPE_CHECKING:
    from .bundler import Bundler


class BundlerManager(object):
    def __init__(self) -> None:
        from .venv_bundler import VenvBundler

        self._bundler_classes: Dict[str, Type["Bundler"]] = {}

        # Register default bundlers
        self.register_bundler_class(VenvBundler)

    def bundler(self, name: str) -> "Bundler":
        if name.lower() not in self._bundler_classes:
            raise BundlerManagerError(
                'The bundler class "{}" does not exist.'.format(name)
            )

        return self._bundler_classes[name.lower()]()

    def register_bundler_class(
        self, bundler_class: Type["Bundler"]
    ) -> "BundlerManager":
        if not bundler_class.name:
            raise BundlerManagerError("A bundler class must have a name")

        if bundler_class.name.lower() in self._bundler_classes:
            raise BundlerManagerError(
                'A bundler class with the name "{}" already exists.'.format(
                    bundler_class.name
                )
            )

        self._bundler_classes[bundler_class.name.lower()] = bundler_class

        return self
