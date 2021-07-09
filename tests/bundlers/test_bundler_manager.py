import pytest

from poetry_bundle_plugin.bundlers.bundler import Bundler
from poetry_bundle_plugin.bundlers.bundler_manager import BundlerManager
from poetry_bundle_plugin.exceptions import BundlerManagerError


class MockBundler(Bundler):

    name = "mock"


def test_bundler_returns_an_instance_of_the_correct_bundler_class():
    manager = BundlerManager()

    bundler = manager.bundler("venv")
    assert isinstance(bundler, Bundler)
    assert "venv" == bundler.name


def test_bundler_raises_an_error_for_incorrect_bundler_classes():
    manager = BundlerManager()

    with pytest.raises(
        BundlerManagerError, match='The bundler class "mock" does not exist.'
    ):
        manager.bundler("mock")


def test_register_bundler_class_registers_new_bundler_classes():
    manager = BundlerManager()
    manager.register_bundler_class(MockBundler)

    bundler = manager.bundler("mock")
    assert isinstance(bundler, Bundler)
    assert "mock" == bundler.name


def test_register_bundler_class_cannot_register_existing_bundler_classes():
    manager = BundlerManager()
    manager.register_bundler_class(MockBundler)

    with pytest.raises(
        BundlerManagerError,
        match='A bundler class with the name "mock" already exists.',
    ):
        manager.register_bundler_class(MockBundler)
