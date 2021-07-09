import shutil
import tempfile

from pathlib import Path

import pytest

from poetry.config.config import Config
from poetry.config.dict_config_source import DictConfigSource
from poetry.utils.env import EnvManager
from poetry.utils.env import VirtualEnv


@pytest.fixture
def config_cache_dir(tmp_dir):
    path = Path(tmp_dir) / ".cache" / "pypoetry"
    path.mkdir(parents=True)
    return path


@pytest.fixture
def config_virtualenvs_path(config_cache_dir):
    return config_cache_dir / "virtualenvs"


@pytest.fixture
def config_source(config_cache_dir):
    source = DictConfigSource()
    source.add_property("cache-dir", str(config_cache_dir))

    return source


@pytest.fixture
def auth_config_source():
    source = DictConfigSource()

    return source


@pytest.fixture
def config(config_source, auth_config_source, mocker):
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
def tmp_dir():
    dir_ = tempfile.mkdtemp(prefix="poetry_bundle_plugin_")

    yield dir_

    shutil.rmtree(dir_)


@pytest.fixture
def tmp_venv(tmp_dir):
    venv_path = Path(tmp_dir) / "venv"

    EnvManager.build_venv(str(venv_path))

    venv = VirtualEnv(venv_path)
    yield venv

    shutil.rmtree(str(venv.path))
