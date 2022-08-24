# Poetry Plugin: Bundle

This package is a plugin that allows the bundling of Poetry projects into various formats.

## Installation

The easiest way to install the `bundle` plugin is via the `self add` command of Poetry.

```bash
poetry self add poetry-plugin-bundle
```

If you used `pipx` to install Poetry you can add the plugin via the `pipx inject` command.

```bash
pipx inject poetry poetry-plugin-bundle
```

Otherwise, if you used `pip` to install Poetry you can add the plugin packages via the `pip install` command.

```bash
pip install poetry-plugin-bundle
```

## Usage

The plugin introduces a `bundle` command namespace that regroups commands to bundle the current project
and its dependencies into various formats. These commands are particularly useful to deploy
Poetry-managed applications.

### bundle venv

### bundle venv

The `bundle venv` command bundles the project and its dependencies into a virtual environment.

The following command

```bash
poetry bundle venv /path/to/environment
```

will bundle the project in the `/path/to/environment` directory by creating the virtual environment,
installing the dependencies and the current project inside it. If the directory does not exist,
it will be created automatically.

By default, the command uses the current Python executable to build the virtual environment.
If you want to use a different one, you can specify it with the `--python/-p` option:

```bash
poetry bundle venv /path/to/environment --python /full/path/to/python
poetry bundle venv /path/to/environment -p python3.8
poetry bundle venv /path/to/environment -p 3.8
```

**Note**

If the virtual environment already exists, two things can happen:

- **The python version of the virtual environment is the same as the main one**: the dependencies will be synced (updated or removed).
- **The python version of the virtual environment is different**: the virtual environment will be recreated from scratch.

You can also ensure that the virtual environment is recreated by using the `--clear` option:

```bash
poetry bundle venv /path/to/environment --clear
```
