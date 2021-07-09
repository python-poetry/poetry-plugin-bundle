from pathlib import Path

from poetry_bundle_plugin.bundlers.venv_bundler import VenvBundler


def test_venv_calls_venv_bundler(app_tester, mocker):
    mock = mocker.patch(
        "poetry_bundle_plugin.bundlers.venv_bundler.VenvBundler.bundle",
        side_effect=[True, False],
    )
    set_path = mocker.spy(VenvBundler, "set_path")
    set_executable = mocker.spy(VenvBundler, "set_executable")
    set_remove = mocker.spy(VenvBundler, "set_remove")

    app_tester.application.catch_exceptions(False)
    assert 0 == app_tester.execute("bundle venv /foo")
    assert 1 == app_tester.execute("bundle venv /foo --python python3.8 --clear")

    assert [
        mocker.call(app_tester.application.poetry, mocker.ANY),
        mocker.call(app_tester.application.poetry, mocker.ANY),
    ] == mock.call_args_list

    assert set_path.call_args_list == [
        mocker.call(mocker.ANY, Path("/foo")),
        mocker.call(mocker.ANY, Path("/foo")),
    ]
    assert set_executable.call_args_list == [
        mocker.call(mocker.ANY, None),
        mocker.call(mocker.ANY, "python3.8"),
    ]
    assert set_remove.call_args_list == [
        mocker.call(mocker.ANY, False),
        mocker.call(mocker.ANY, True),
    ]
