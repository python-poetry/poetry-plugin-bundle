from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.console.application import Application
from poetry.core.toml.file import TOMLFile
from poetry.factory import Factory
from poetry.packages import Locker


if TYPE_CHECKING:
    from pathlib import Path

    from poetry.poetry import Poetry


class TestApplication(Application):
    def __init__(self, poetry: Poetry) -> None:
        super().__init__()
        self._poetry = poetry

    def reset_poetry(self) -> None:
        poetry = self._poetry
        self._poetry = Factory().create_poetry(self._poetry.file.path.parent)
        self._poetry.set_pool(poetry.pool)
        self._poetry.set_config(poetry.config)
        self._poetry.set_locker(
            TestLocker(poetry.locker.lock.path, self._poetry.local_config)
        )


class TestLocker(Locker):
    def __init__(self, lock: str | Path, local_config: dict) -> None:
        self._lock = TOMLFile(lock)
        self._local_config = local_config
        self._lock_data: dict | None = None
        self._content_hash = self._get_content_hash()
        self._locked = False
        self._lock_data = None
        self._write = False

    def write(self, write: bool = True) -> None:
        self._write = write

    def is_locked(self) -> bool:
        return self._locked

    def locked(self, is_locked: bool = True) -> TestLocker:
        self._locked = is_locked

        return self

    def mock_lock_data(self, data: dict) -> None:
        self.locked()

        self._lock_data = data

    def is_fresh(self) -> bool:
        return True

    def _write_lock_data(self, data: dict) -> None:
        if self._write:
            super()._write_lock_data(data)
            self._locked = True
            return

        self._lock_data = data
