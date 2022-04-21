from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from cleo.events.console_events import COMMAND
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_plugin_bundle.console.commands.bundle.venv import BundleVenvCommand


if TYPE_CHECKING:
    from cleo.events.console_command_event import ConsoleCommandEvent
    from poetry.console.application import Application
    from poetry.console.commands.command import Command


class BundleApplicationPlugin(ApplicationPlugin):
    @property
    def commands(self) -> list[type[Command]]:
        return [BundleVenvCommand]

    def activate(self, application: Application) -> None:
        application.event_dispatcher.add_listener(
            COMMAND, self.configure_bundle_commands
        )
        super().activate(application=application)

    def configure_bundle_commands(
        self, event: ConsoleCommandEvent, event_name: str, _: Any
    ) -> None:
        from poetry_plugin_bundle.console.commands.bundle.bundle_command import (
            BundleCommand,
        )

        command: BundleCommand = cast(BundleCommand, event.command)
        if not isinstance(command, BundleCommand):
            return

        # If the command already has a bundler manager, do nothing
        if command.bundler_manager is not None:
            return

        from poetry_plugin_bundle.bundlers.bundler_manager import BundlerManager

        command.set_bundler_manager(BundlerManager())
