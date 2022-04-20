from __future__ import annotations

import shutil
import tempfile

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Iterator

import pytest

from poetry.config.config import Config
from poetry.config.dict_config_source import DictConfigSource
from poetry.utils.env import EnvManager
from poetry.utils.env import VirtualEnv


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def config_cache_dir(tmp_dir: str) -> Path:
    path = Path(tmp_dir) / ".cache" / "pypoetry"
    path.mkdir(parents=True)
    return path


@pytest.fixture
def config_virtualenvs_path(config_cache_dir: Path) -> Path:
    return config_cache_dir / "virtualenvs"


@pytest.fixture
def config_source(config_cache_dir: Path) -> DictConfigSource:
    source = DictConfigSource()
    source.add_property("cache-dir", str(config_cache_dir))

    return source


@pytest.fixture
def auth_config_source() -> DictConfigSource:
    source = DictConfigSource()

    return source


@pytest.fixture
def config(
    config_source: DictConfigSource,
    auth_config_source: DictConfigSource,
    mocker: MockerFixture,
) -> Config:
    import keyring

    from keyring.backends.fail import Keyring

    keyring.set_keyring(Keyring())

    c = Config()
    c.merge(config_source.config)
    c.set_config_source(config_source)
    c.set_auth_config_source(auth_config_source)

    mocker.patch("poetry.factory.Factory.create_config", return_value=c)
    mocker.patch("poetry.config.config.Config.set_config_source")

    return c


@pytest.fixture
def tmp_dir() -> Iterator[str]:
    dir_ = tempfile.mkdtemp(prefix="poetry_plugin_bundle_")

    yield dir_

    shutil.rmtree(dir_)


@pytest.fixture
def tmp_venv(tmp_dir: str) -> Iterator[VirtualEnv]:
    venv_path = Path(tmp_dir) / "venv"

    EnvManager.build_venv(str(venv_path))

    venv = VirtualEnv(venv_path)
    yield venv

    shutil.rmtree(str(venv.path))
