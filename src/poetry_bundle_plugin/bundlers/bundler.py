from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.poetry import Poetry


class Bundler(object):

    name: str

    def bundle(self, poetry: "Poetry", io: "IO") -> None:
        raise NotImplementedError()
