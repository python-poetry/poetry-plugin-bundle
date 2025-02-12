from __future__ import annotations

import shutil
import sys

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from cleo.formatters.style import Style
from cleo.io.buffered_io import BufferedIO
from poetry.core.packages.package import Package
from poetry.core.packages.utils.link import Link
from poetry.factory import Factory
from poetry.installation.operations.install import Install
from poetry.puzzle.exceptions import SolverProblemError
from poetry.repositories.repository import Repository
from poetry.repositories.repository_pool import RepositoryPool
from poetry.utils.env import EnvManager
from poetry.utils.env import MockEnv
from poetry.utils.env import VirtualEnv

from poetry_plugin_bundle.bundlers.venv_bundler import VenvBundler


if TYPE_CHECKING:
    from poetry.config.config import Config
    from poetry.poetry import Poetry
    from pytest_mock import MockerFixture


@pytest.fixture()
def io() -> BufferedIO:
    io = BufferedIO()

    io.output.formatter.set_style("success", Style("green", options=["dark"]))
    io.output.formatter.set_style("warning", Style("yellow", options=["dark"]))

    return io


@pytest.fixture()
def poetry(config: Config) -> Poetry:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "simple_project"
    )
    poetry.set_config(config)

    pool = RepositoryPool()
    repository = Repository("repo")
    repository.add_package(Package("foo", "1.0.0"))
    pool.add_repository(repository)
    poetry.set_pool(pool)

    return poetry


def _create_venv_marker_file(tempdir: str | Path) -> Path:
    marker_file = Path(tempdir) / "existing-venv-marker.txt"
    marker_file.write_text("This file should get deleted as part of venv recreation.")
    return marker_file


def test_bundler_should_build_a_new_venv_with_existing_python(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture
) -> None:
    shutil.rmtree(tmpdir)
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))

    assert bundler.bundle(poetry, io)

    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {tmpdir}
"""
    assert expected == io.fetch_output()


def test_bundler_should_build_a_new_venv_with_given_executable(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture
) -> None:
    shutil.rmtree(tmpdir)
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))
    bundler.set_executable(sys.executable)

    assert bundler.bundle(poetry, io)

    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Python {sys.executable}
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {tmpdir}
"""
    assert expected == io.fetch_output()


def test_bundler_should_build_a_new_venv_if_existing_venv_is_incompatible(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture
) -> None:
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    mock_env = MockEnv(path=Path(tmpdir), is_venv=True, version_info=(1, 2, 3))
    mocker.patch("poetry.utils.env.EnvManager.get", return_value=mock_env)

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))

    marker_file = _create_venv_marker_file(tmpdir)

    assert marker_file.exists()
    assert bundler.bundle(poetry, io)
    assert not marker_file.exists()

    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {tmpdir}: Replacing existing virtual environment due to incompatible Python version
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {tmpdir}
"""
    assert expected == io.fetch_output()


def test_bundler_should_use_an_existing_venv_if_compatible(
    io: BufferedIO, tmp_venv: VirtualEnv, poetry: Poetry, mocker: MockerFixture
) -> None:
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(tmp_venv.path)

    marker_file = _create_venv_marker_file(tmp_venv.path)

    assert marker_file.exists()
    assert bundler.bundle(poetry, io)
    assert marker_file.exists()

    path = str(tmp_venv.path)
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""
    assert expected == io.fetch_output()


def test_bundler_should_remove_an_existing_venv_if_forced(
    io: BufferedIO, tmp_venv: VirtualEnv, poetry: Poetry, mocker: MockerFixture
) -> None:
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(tmp_venv.path)
    bundler.set_remove(True)

    marker_file = _create_venv_marker_file(tmp_venv.path)

    assert marker_file.exists()
    assert bundler.bundle(poetry, io)
    assert not marker_file.exists()

    path = str(tmp_venv.path)
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""
    assert expected == io.fetch_output()


def test_bundler_should_fail_when_installation_fails(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture
) -> None:
    mocker.patch(
        "poetry.installation.executor.Executor._do_execute_operation",
        side_effect=Exception(),
    )

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))

    assert not bundler.bundle(poetry, io)

    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Failed at step Installing dependencies
"""
    assert expected == io.fetch_output()


def test_bundler_should_display_a_warning_for_projects_with_no_module(
    io: BufferedIO, tmp_venv: VirtualEnv, mocker: MockerFixture, config: Config
) -> None:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "simple_project_with_no_module"
    )
    poetry.set_config(config)

    pool = RepositoryPool()
    repository = Repository("repo")
    repository.add_package(Package("foo", "1.0.0"))
    pool.add_repository(repository)
    poetry.set_pool(pool)

    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(tmp_venv.path)
    bundler.set_remove(True)

    assert bundler.bundle(poetry, io)

    path = str(tmp_venv.path)
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
  • The root package was not installed because no matching module or package was found.
"""
    assert expected == io.fetch_output()


def test_bundler_can_filter_dependency_groups(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture, config: Config
) -> None:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "simple_project_with_dev_dep"
    )
    poetry.set_config(config)

    # foo is in the main dependency group
    # bar is a dev dependency
    # add a repository for foo but not bar
    pool = RepositoryPool()
    repository = Repository("repo")
    repository.add_package(Package("foo", "1.0.0"))
    pool.add_repository(repository)
    poetry.set_pool(pool)

    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))
    bundler.set_remove(True)

    # This should fail because there is not repo for bar
    with pytest.raises(SolverProblemError):
        assert not bundler.bundle(poetry, io)

    bundler.set_activated_groups({"main"})
    io.clear_output()

    # This succeeds because the dev dependency group is filtered out
    assert bundler.bundle(poetry, io)

    path = tmpdir
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""
    assert expected == io.fetch_output()


@pytest.mark.parametrize("compile", [True, False])
def test_bundler_passes_compile_flag(
    io: BufferedIO,
    tmp_venv: VirtualEnv,
    poetry: Poetry,
    mocker: MockerFixture,
    compile: bool,
) -> None:
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(tmp_venv.path)
    bundler.set_remove(True)
    bundler.set_compile(compile)

    # bundle passes the flag from set_compile to enable_bytecode_compilation method
    mocker = mocker.patch(
        "poetry.installation.executor.Executor.enable_bytecode_compilation"
    )

    assert bundler.bundle(poetry, io)

    mocker.assert_called_once_with(compile)

    path = str(tmp_venv.path)
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""
    assert expected == io.fetch_output()


def test_bundler_editable_deps(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture, config: Config
) -> None:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "simple_project_with_editable_dep"
    )
    poetry.set_config(config)

    install_spy = mocker.spy(Install, "__init__")
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))

    io.clear_output()

    bundler.bundle(poetry, io)

    path = tmpdir
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""
    assert expected == io.fetch_output()

    installed_packages = [call.args[1] for call in install_spy.call_args_list]
    dep_installs = list(
        filter(lambda package: package.name == "bar", installed_packages)
    )
    assert len(dep_installs) > 0

    editable_installs = list(filter(lambda package: package.develop, dep_installs))
    assert len(editable_installs) == 0


def test_bundler_should_build_a_venv_at_specified_path_if_centralized_venv_exists(
    io: BufferedIO,
    tmpdir: str,
    tmp_venv: VirtualEnv,
    poetry: Poetry,
    mocker: MockerFixture,
) -> None:
    """
    Test coverage for [Issue #112](https://github.com/python-poetry/poetry-plugin-bundle/issues/112), which involves
    a pre-existing "centralized" venv at the path specified in the Poetry configuration.
    The test is intended to verify that the VenvBundler will build a new venv at the specified path if a centralized
    venv already exists.
    """
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    poetry.config.config["virtualenvs"]["in-project"] = False
    poetry.config.config["virtualenvs"]["path"] = tmp_venv.path

    env_manager = EnvManager(poetry)
    env_manager.activate(sys.executable)

    bundler_venv_path = Path(tmpdir) / "bundler"
    bundler = VenvBundler()
    bundler.set_path(bundler_venv_path)

    assert bundler.bundle(poetry, io)

    bundler_venv = VirtualEnv(bundler_venv_path)
    assert bundler_venv.is_sane()

    path = bundler_venv_path
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""
    assert expected == io.fetch_output()


def test_bundler_non_package_mode(
    io: BufferedIO, tmp_venv: VirtualEnv, mocker: MockerFixture, config: Config
) -> None:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "non_package_mode"
    )
    poetry.set_config(config)

    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(tmp_venv.path)
    bundler.set_remove(True)

    assert bundler.bundle(poetry, io)

    path = str(tmp_venv.path)
    expected = f"""\
  • Bundling simple-project-non-package-mode (1.2.3) into {path}
  • Bundling simple-project-non-package-mode (1.2.3) into {path}: Creating a virtual environment using Poetry-determined Python
  • Bundling simple-project-non-package-mode (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project-non-package-mode (1.2.3) into {path}: Skipping installation for non package project simple-project-non-package-mode
  • Bundled simple-project-non-package-mode (1.2.3) into {path}
"""
    assert expected == io.fetch_output()


def test_bundler_platform_override(
    io: BufferedIO, tmpdir: str, mocker: MockerFixture, config: Config
) -> None:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "project_with_binary_wheel"
    )
    poetry.set_config(config)

    def get_links_fake(package: Package) -> list[Link]:
        return [Link(f"https://example.com/{file['file']}") for file in package.files]

    mocker.patch(
        "poetry.installation.chooser.Chooser._get_links", side_effect=get_links_fake
    )
    mocker.patch("poetry.installation.executor.Executor._execute_uninstall")
    mocker.patch("poetry.installation.executor.Executor._execute_update")
    mock_download_link = mocker.patch(
        "poetry.installation.executor.Executor._download_link"
    )
    mocker.patch("poetry.installation.wheel_installer.WheelInstaller.install")

    def get_installed_links() -> dict[str, str]:
        return {
            call[0][0].package.name: call[0][1].filename
            for call in mock_download_link.call_args_list
        }

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))
    bundler.set_remove(True)

    bundler.set_platform("manylinux_2_28_x86_64")
    bundler.bundle(poetry, io)
    installed_link_by_package = get_installed_links()
    assert "manylinux_2_28_x86_64" in installed_link_by_package["cryptography"]
    assert "manylinux_2_17_x86_64" in installed_link_by_package["cffi"]
    assert "py3-none-any.whl" in installed_link_by_package["pycparser"]

    bundler.set_platform("manylinux2014_x86_64")
    bundler.bundle(poetry, io)
    installed_link_by_package = get_installed_links()
    assert "manylinux2014_x86_64" in installed_link_by_package["cryptography"]
    assert "manylinux_2_17_x86_64" in installed_link_by_package["cffi"]
    assert "py3-none-any.whl" in installed_link_by_package["pycparser"]

    bundler.set_platform("macosx_10_9_x86_64")
    bundler.bundle(poetry, io)
    installed_link_by_package = get_installed_links()
    assert "macosx_10_9_universal2" in installed_link_by_package["cryptography"]
    expected_cffi_platform = (
        "macosx_10_9_x86_64" if sys.version_info < (3, 13) else "cffi-1.17.1.tar.gz"
    )
    assert expected_cffi_platform in installed_link_by_package["cffi"]
    assert "py3-none-any.whl" in installed_link_by_package["pycparser"]

    bundler.set_platform("macosx_11_0_arm64")
    bundler.bundle(poetry, io)
    installed_link_by_package = get_installed_links()
    assert "macosx_10_9_universal2" in installed_link_by_package["cryptography"]
    expected_cffi_platform = (
        "macosx_11_0_arm64" if sys.version_info >= (3, 9) else "cffi-1.17.1.tar.gz"
    )
    assert expected_cffi_platform in installed_link_by_package["cffi"]
    assert "py3-none-any.whl" in installed_link_by_package["pycparser"]

    bundler.set_platform("musllinux_1_2_aarch64")
    bundler.bundle(poetry, io)
    installed_link_by_package = get_installed_links()
    assert "musllinux_1_2_aarch64" in installed_link_by_package["cryptography"]
    expected_cffi_platform = (
        "musllinux_1_1_aarch64" if sys.version_info >= (3, 9) else "cffi-1.17.1.tar.gz"
    )
    assert expected_cffi_platform in installed_link_by_package["cffi"]
    assert "py3-none-any.whl" in installed_link_by_package["pycparser"]
