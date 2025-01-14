# Poetry Plugin: Bundle

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

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

The `bundle venv` command bundles the project and its dependencies into a virtual environment.

The following command

```bash
poetry bundle venv /path/to/environment
```

will bundle the project in the `/path/to/environment` directory by creating the virtual environment,
installing the dependencies and the current project inside it. If the directory does not exist,
it will be created automatically.

By default, the command uses the same Python executable that Poetry would use
when running `poetry install` to build the virtual environment.
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

#### --platform option (Experimental)
This option allows you to specify a target platform for binary wheel selection, allowing you to install wheels for
architectures/platforms other than the host system.

The primary use case is in CI/CD operations to produce a deployable asset, such as a ZIP file for AWS Lambda and other
such cloud providers. It is common for the runtimes of these target environments to be different enough from the CI/CD's
runner host such that the binary wheels selected using the host's criteria are not compatible with the target system's.

#### Supported platform values
The `--platform` option requires a value that conforms to the [Python Packaging Platform Tag format](
https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#platform-tag). Only the following
"families" are supported at this time:
- `manylinux`
- `musllinux`
- `macosx`

#### Examples of valid platform tags
This is not a comprehensive list, but illustrates typical examples.

`manylinux_2_28_x86_64`, `manylinux1_x86_64`, `manylinux2010_x86_64`, `manylinux2014_x86_64`

`musllinux_1_2_x86_64`

`macosx_10_9_x86_64`, `macosx_10_9_intel`, `macosx_11_1_universal2`, `macosx_11_0_arm64`

#### Example use case for AWS Lambda
As an example of one motivating use case for this option, consider the AWS Lambda "serverless" execution environment.
Depending upon which Python version you configure for your runtime, you may get different versions of the Linux system
runtime.  When dealing with pre-compiled binary wheels, these runtime differences can matter.  If a shared library from
a wheel is packaged in your deployment artifact that is incompatible with the runtime provided environment, then your
Python "function" will error at execution time in the serverless environment.
The issue arises when the build system that is producing the deployment artifact has a materially different platform
from the selected serverless Lambda runtime.

For example, the Python 3.11 Lambda runtime is Amazon Linux 2, which includes the Glibc 2.26 library.  If a Python
application is packaged and deployed in this environment that contains wheels built for a more recent version of Glibc,
then a runtime error will result.  This is likely to occur even if the build system is the same CPU architecture
(e.g. x86_64) and core platform (e.g. Linux) and there is a package dependency that provides multiple precompiled
wheels for various Glibc (or other system library) versions.  The "best" wheel in the context of the build system can
differ from that of the target execution environment.


#### Limitations
**This is not an actual cross-compiler**.  Nor is it a containerized compilation/build environment. It simply allows
controlling which **prebuilt** binaries are selected.  It is not a replacement for cross-compilation or containerized
builds for use cases requiring that.

If there is not a binary wheel distribution compatible with the specified platform, then the package's source
distribution is selected.  If there are compile/build steps for "extensions" that need to run for the source
distribution, then these operations will execute in the context of the host CI/build system.
**This means that the `--platform` option
has no impact on any extension compile/build operations that must occur during package installation.**
This feature is only for
**selecting** prebuilt wheels, and **not for compiling** them from source.

Arguably, in a vast number of use cases, prebuilt wheel binaries are available for your packages and simply selecting
them based on a platform other than the host CI/build system is much faster and simpler than heavier build-from-source
alternatives.
