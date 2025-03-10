# Change Log


## [1.7.0] - 2025-03-10

### Added

- Add experimental `--platform` option to facilitate installing wheels for platforms other than the host system ([#123](https://github.com/python-poetry/poetry-plugin-bundle/pull/123)).


## [1.6.0] - 2025-02-16

### Added

- Ensure compatibility with Poetry 2.1 ([#137](https://github.com/python-poetry/poetry-plugin-bundle/pull/137)).

### Changed

- Drop support for older Poetry versions ([#137](https://github.com/python-poetry/poetry-plugin-bundle/pull/137)).


## [1.5.0] - 2025-01-05

### Added

- Ensure compatibility with Poetry 2.0 ([#128](https://github.com/python-poetry/poetry-plugin-bundle/pull/128)).
- Add support for projects with `package-mode = false` ([#119](https://github.com/python-poetry/poetry-plugin-bundle/pull/119)).

### Changed

- Drop support for Python 3.8 ([#127](https://github.com/python-poetry/poetry-plugin-bundle/pull/127)).


## [1.4.1] - 2024-08-15

### Fixed

- Fix an issue where `path/to/venv` was ignored and an existing venv was used instead ([#114](https://github.com/python-poetry/poetry-plugin-bundle/pull/114)).


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


[Unreleased]: https://github.com/python-poetry/poetry-plugin-bundle/compare/1.7.0...main
[1.7.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.7.0
[1.6.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.6.0
[1.5.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.5.0
[1.4.1]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.4.1
[1.4.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.4.0
[1.3.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.3.0
[1.2.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.2.0
[1.1.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.1.0
[1.0.0]: https://github.com/python-poetry/poetry-plugin-bundle/releases/tag/1.0.0
