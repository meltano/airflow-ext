import os
import sys
from typing import List

import structlog
import typer

from airflow_extension.airflow import Airflow
from meltano_extension_sdk.extension import DescribeFormat
from meltano_extension_sdk.logging import default_logging_config, parse_log_level

log = structlog.get_logger()

APP_NAME: str = "airflow_extension"

plugin = Airflow()

typer.core.rich = None # remove to enable stylized help output when `rich` is installed
app = typer.Typer(pretty_exceptions_enable=False, rich_markup_mode=None)

@app.command()
def initialize(ctx: typer.Context, force: bool = False):
    """Initialize the plugin.

    This will create the airflow.cfg, initialize the database, and install the meltano airflow dag generator.
    """
    try:
        plugin.initialize(force)
    except Exception:
        log.exception(
            "initialize failed with uncaught exception, please report exception to maintainer"
        )
        sys.exit(1)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def invoke(ctx: typer.Context, command_args: List[str]):
    """Invoke the plugin.

    Note: that if a command argument is a list, such as command_args, then
    unknown options are also included in the list and NOT stored in the context as usual.

    Args:
        ctx: The typer.Context for this invocation
        command_args: The command args to invoke
    """
    command_name, command_args = command_args[0], command_args[1:]
    log.debug(
        "called", command_name=command_name, command_args=command_args, env=os.environ
    )

    try:
        plugin.pre_invoke()
    except Exception:
        log.exception(
            "pre_invoke failed with uncaught exception, please report exception to maintainer"
        )
        sys.exit(1)

    try:
        plugin.invoke(command_name, command_args)
    except Exception:
        log.exception(
            "invoke failed with uncaught exception, please report exception to maintainer"
        )
        sys.exit(1)

    try:
        plugin.post_invoke()
    except Exception:
        log.exception(
            "ppost_invoke failed with uncaught exception, please report exception to maintainer"
        )
        sys.exit(1)


@app.command()
def describe(
    output_format: DescribeFormat = typer.Option(
        DescribeFormat.text, "--format", help="Output format"
    )
):
    """Describe the available commands of this extension."""
    try:
        typer.echo(plugin.describe_formatted(output_format))
    except Exception:
        log.exception(
            "describe failed with uncaught exception, please report exception to maintainer"
        )
        sys.exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_level: str = typer.Option("INFO", envvar="LOG_LEVEL"),
    log_timestamps: bool = typer.Option(
        False, envvar="LOG_TIMESTAMPS", help="Show timestamp in logs"
    ),
    log_levels: bool = typer.Option(
        False, "--log-levels", envvar="LOG_LEVELS", help="Show log levels"
    ),
    meltano_log_json: bool = typer.Option(
        False,
        "--meltano-log-json",
        envvar="MELTANO_LOG_JSON",
        help="Log in the meltano JSON log format",
    ),
):
    """
    Simple Meltano extension to wrap the airflow CLI.
    """
    default_logging_config(
        level=parse_log_level(log_level),
        timestamps=log_timestamps,
        levels=log_levels,
        json_format=meltano_log_json,
    )
