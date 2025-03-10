from __future__ import annotations

import tempfile

from pathlib import Path
from typing import TYPE_CHECKING

from cleo.io.null_io import NullIO

from poetry_plugin_bundle.bundlers.venv_bundler import VenvBundler


if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.poetry import Poetry
    from typing_extensions import Self


class ArchiveBundler(VenvBundler):
    name = "archive"

    def __init__(self) -> None:
        super().__init__()
        self._ar_path = Path("output")
        self._format = "zip"
        self._site_packages_only = False

    def set_path(self, path: Path) -> Self:
        self._ar_path = path
        return self

    def set_format(self, ar_format: str) -> Self:
        self._format = ar_format

        return self

    def set_site_packages_only(self, value: bool) -> Self:
        self._site_packages_only = value

        return self

    def bundle(self, poetry: Poetry, io: IO) -> bool:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._path = Path(temp_dir)

            if not super().bundle(poetry, NullIO()):
                return False

            import shutil

            dir_path = self._path
            if self._site_packages_only:
                dir_path = dir_path.joinpath("Lib", "site-packages")

            self._write(
                io, f"Creating archive {self._ar_path} using format {self._format}"
            )

            try:
                shutil.make_archive(str(self._ar_path), self._format, dir_path)
            except (ValueError, PermissionError) as e:
                self._write(io, f"Error while creating archive: <red>{e!s}</red>")
                return False

        return True
