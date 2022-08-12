from __future__ import annotations

import pkgutil
import os
import subprocess
import sys

import structlog

from meltano_extension_sdk.extension import Description, ExtensionBase
from meltano_extension_sdk.process import Invoker, log_subprocess_error

log = structlog.get_logger()


class {{ cookiecutter.source_name }}(ExtensionBase):

    def __init__(self):
        self.{{ cookiecutter.extension_name }}_bin = "{{ cookiecutter.wrapper_target_name }}" # verify this is the correct name
        self.{{ cookiecutter.extension_name }}_invoker = Invoker(self.{{ cookiecutter.extension_name }}_bin, env=os.environ.copy())

    def invoke(self, command_name: str | None, *command_args):
        """Invoke the underlying cli, that is being wrapped by this extension."""
        try:
            self.{{ cookiecutter.extension_name }}_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"{{ cookiecutter.extension_name }} {command_name}", err, "{{ cookiecutter.extension_name }} invocation failed"
            )
            sys.exit(err.returncode)

    def describe(self) -> Description:
        """Return a description of the extension."""
        # simply list what custom commands you'd like to make available
        # or use ":splat" to indicate that you're extension supports wild card pass-through.
        return Description(commands=[":splat"])