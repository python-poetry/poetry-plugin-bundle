from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from cleo.testers.application_tester import ApplicationTester
from poetry.factory import Factory

from tests.helpers import TestApplication
from tests.helpers import TestLocker


if TYPE_CHECKING:
    from poetry.config.config import Config
    from poetry.poetry import Poetry


@pytest.fixture
def project_directory() -> str:
    return "simple_project"


@pytest.fixture
def poetry(project_directory: str, config: Config) -> Poetry:
    p = Factory().create_poetry(
        Path(__file__).parent.parent / "fixtures" / project_directory
    )
    p.set_locker(TestLocker(p.locker.lock.path, p.locker._local_config))

    return p


@pytest.fixture
def app(poetry: Poetry) -> TestApplication:
    app_ = TestApplication(poetry)

    return app_


@pytest.fixture
def app_tester(app: TestApplication) -> ApplicationTester:
    return ApplicationTester(app)
