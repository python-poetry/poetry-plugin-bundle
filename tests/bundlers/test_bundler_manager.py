from __future__ import annotations

import pytest

from poetry_plugin_bundle.bundlers.bundler import Bundler
from poetry_plugin_bundle.bundlers.bundler_manager import BundlerManager
from poetry_plugin_bundle.exceptions import BundlerManagerError


class MockBundler(Bundler):
    name = "mock"


def test_bundler_returns_an_instance_of_the_correct_bundler_class() -> None:
    manager = BundlerManager()

    bundler = manager.bundler("venv")
    assert isinstance(bundler, Bundler)
    assert bundler.name == "venv"


def test_bundler_raises_an_error_for_incorrect_bundler_classes() -> None:
    manager = BundlerManager()

    with pytest.raises(
        BundlerManagerError, match='The bundler class "mock" does not exist.'
    ):
        manager.bundler("mock")


def test_register_bundler_class_registers_new_bundler_classes() -> None:
    manager = BundlerManager()
    manager.register_bundler_class(MockBundler)

    bundler = manager.bundler("mock")
    assert isinstance(bundler, Bundler)
    assert bundler.name == "mock"


def test_register_bundler_class_cannot_register_existing_bundler_classes() -> None:
    manager = BundlerManager()
    manager.register_bundler_class(MockBundler)

    with pytest.raises(
        BundlerManagerError,
        match='A bundler class with the name "mock" already exists.',
    ):
        manager.register_bundler_class(MockBundler)
