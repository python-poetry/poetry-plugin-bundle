# Change Log


## [1.4.0] - 2024-07-26

### Added

- Add a `--compile` option analogous to `poetry install` ([#88](https://github.com/python-poetry/poetry-plugin-bundle/pull/88)).

### Changed

- Drop support for Python 3.7 ([#66](https://github.com/python-poetry/poetry-plugin-bundle/pull/66)).
- Install all dependencies as non-editable ([#106](https://github.com/python-poetry/poetry-plugin-bundle/pull/106)).
- Use same logic as `poetry install` to determine the Python version if not provided explicitly ([#103](https://github.com/python-poetry/poetry-plugin-bundle/pull/103)).


## [1.3.0] - 2023-05-29

### Added

- Ensure compatibility with poetry 1.5 ([#61](https://github.com/python-poetry/poetry-plugin-bundle/pull/61)).


## [1.2.0] - 2023-03-19

### Added

- Ensure compatibility with poetry 1.4 ([#48](https://github.com/python-poetry/poetry-plugin-bundle/pull/48)).

### Changed

- Drop some compatibility code and bump minimum required poetry version to 1.4.0 ([#48](https://github.com/python-poetry/poetry-plugin-bundle/pull/48)).


## [1.1.0] - 2022-11-04

### Added

- Add support for dependency groups ([#26](https://github.com/python-poetry/poetry-plugin-bundle/pull/26)).


## [1.0.0] - 2022-08-24

Initial version.


[Unreleased]: https://github.com/python-poetry/poetry-plugin-bundle/compare/1.4.0...main
[1.4.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.4.0
[1.3.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.3.0
[1.2.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.2.0
[1.1.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.1.0
[1.0.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.0.0
