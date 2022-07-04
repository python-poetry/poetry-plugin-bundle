from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.poetry import Poetry


class Bundler:
    name: str

    def bundle(self, poetry: Poetry, io: IO) -> bool:
        raise NotImplementedError()
