from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import cast

from cleo.events.console_events import COMMAND
from poetry.console.commands.command import Command
from poetry.plugins.application_plugin import ApplicationPlugin


if TYPE_CHECKING:
    from cleo.events.console_command_event import ConsoleCommandEvent
    from poetry.console.application import Application


def load_command(name: str) -> Callable:
    def _load() -> type[Command]:
        module = import_module(
            f"poetry_bundle_plugin.console.commands.{'.'.join(name.split(' '))}"
        )
        command_class = getattr(
            module, f"{''.join(c.title() for c in name.split(' '))}Command"
        )

        return command_class()

    return _load


COMMANDS = ["bundle venv"]


class BundleApplicationPlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        application.event_dispatcher.add_listener(
            COMMAND, self.configure_bundle_commands
        )

        for command in COMMANDS:
            application.command_loader.register_factory(command, load_command(command))

    def configure_bundle_commands(
        self, event: ConsoleCommandEvent, event_name: str, _: Any
    ) -> None:
        from poetry_bundle_plugin.console.commands.bundle.bundle_command import (
            BundleCommand,
        )

        command: BundleCommand = cast(BundleCommand, event.command)
        if not isinstance(command, BundleCommand):
            return

        # If the command already has a bundler manager, do nothing
        if command.bundler_manager is not None:
            return

        from poetry_bundle_plugin.bundlers.bundler_manager import BundlerManager

        command.set_bundler_manager(BundlerManager())
