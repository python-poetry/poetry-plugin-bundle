from __future__ import annotations

from typing import TYPE_CHECKING

from poetry_bundle_plugin.exceptions import BundlerManagerError


if TYPE_CHECKING:
    from poetry_bundle_plugin.bundlers.bundler import Bundler


class BundlerManager:
    def __init__(self) -> None:
        from poetry_bundle_plugin.bundlers.venv_bundler import VenvBundler

        self._bundler_classes: dict[str, type[Bundler]] = {}

        # Register default bundlers
        self.register_bundler_class(VenvBundler)

    def bundler(self, name: str) -> Bundler:
        if name.lower() not in self._bundler_classes:
            raise BundlerManagerError(f'The bundler class "{name}" does not exist.')

        return self._bundler_classes[name.lower()]()

    def register_bundler_class(self, bundler_class: type[Bundler]) -> BundlerManager:
        if not bundler_class.name:
            raise BundlerManagerError("A bundler class must have a name")

        if bundler_class.name.lower() in self._bundler_classes:
            raise BundlerManagerError(
                f'A bundler class with the name "{bundler_class.name}" already exists.'
            )

        self._bundler_classes[bundler_class.name.lower()] = bundler_class

        return self
