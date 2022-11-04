from __future__ import annotations

import shutil
import sys

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from cleo.formatters.style import Style
from cleo.io.buffered_io import BufferedIO
from poetry.core.packages.package import Package
from poetry.factory import Factory
from poetry.puzzle.exceptions import SolverProblemError
from poetry.repositories.pool import Pool
from poetry.repositories.repository import Repository

from poetry_plugin_bundle.bundlers.venv_bundler import VenvBundler


if TYPE_CHECKING:
    from poetry.config.config import Config
    from poetry.poetry import Poetry
    from poetry.utils.env import VirtualEnv
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

    pool = Pool()
    repository = Repository("repo")
    repository.add_package(Package("foo", "1.0.0"))
    pool.add_repository(repository)
    poetry.set_pool(pool)

    return poetry


def test_bundler_should_build_a_new_venv_with_existing_python(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture
) -> None:
    shutil.rmtree(tmpdir)
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))

    assert bundler.bundle(poetry, io)

    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {tmpdir}
"""  # noqa: E501
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

    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {tmpdir}
"""  # noqa: E501
    assert expected == io.fetch_output()


def test_bundler_should_build_a_new_venv_if_existing_venv_is_incompatible(
    io: BufferedIO, tmpdir: str, poetry: Poetry, mocker: MockerFixture
) -> None:
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(Path(tmpdir))

    assert bundler.bundle(poetry, io)

    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Removing existing virtual environment
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {tmpdir}
"""  # noqa: E501
    assert expected == io.fetch_output()


def test_bundler_should_use_an_existing_venv_if_compatible(
    io: BufferedIO, tmp_venv: VirtualEnv, poetry: Poetry, mocker: MockerFixture
) -> None:
    mocker.patch("poetry.installation.executor.Executor._execute_operation")

    bundler = VenvBundler()
    bundler.set_path(tmp_venv.path)

    assert bundler.bundle(poetry, io)

    path = str(tmp_venv.path)
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Using existing virtual environment
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

    assert bundler.bundle(poetry, io)

    path = str(tmp_venv.path)
    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Removing existing virtual environment
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""  # noqa: E501
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

    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {tmpdir}
  • Bundling simple-project (1.2.3) into {tmpdir}: Removing existing virtual environment
  • Bundling simple-project (1.2.3) into {tmpdir}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {tmpdir}: Installing dependencies
  • Bundling simple-project (1.2.3) into {tmpdir}: Failed at step Installing dependencies
"""  # noqa: E501
    assert expected == io.fetch_output()


def test_bundler_should_display_a_warning_for_projects_with_no_module(
    io: BufferedIO, tmp_venv: VirtualEnv, mocker: MockerFixture, config: Config
) -> None:
    poetry = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / "simple_project_with_no_module"
    )
    poetry.set_config(config)

    pool = Pool()
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
    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Removing existing virtual environment
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
  • The root package was not installed because no matching module or package was found.
"""  # noqa: E501
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
    pool = Pool()
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
    python_version = ".".join(str(v) for v in sys.version_info[:3])
    expected = f"""\
  • Bundling simple-project (1.2.3) into {path}
  • Bundling simple-project (1.2.3) into {path}: Removing existing virtual environment
  • Bundling simple-project (1.2.3) into {path}: Creating a virtual environment using Python {python_version}
  • Bundling simple-project (1.2.3) into {path}: Installing dependencies
  • Bundling simple-project (1.2.3) into {path}: Installing simple-project (1.2.3)
  • Bundled simple-project (1.2.3) into {path}
"""  # noqa: E501
    assert expected == io.fetch_output()
