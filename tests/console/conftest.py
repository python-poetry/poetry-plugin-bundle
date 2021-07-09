from pathlib import Path

import pytest

from cleo.testers.application_tester import ApplicationTester
from poetry.factory import Factory

from tests.helpers import TestApplication
from tests.helpers import TestLocker


@pytest.fixture
def project_directory():
    return "simple_project"


@pytest.fixture
def poetry(project_directory, config):
    p = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / project_directory
    )
    p.set_locker(TestLocker(p.locker.lock.path, p.locker._local_config))

    return p


@pytest.fixture
def app(poetry):
    app_ = TestApplication(poetry)

    return app_


@pytest.fixture
def app_tester(app):
    return ApplicationTester(app)
