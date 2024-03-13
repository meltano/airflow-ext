"""Passthrough shim for airflow extension."""

import sys

import structlog
from meltano.edk.logging import pass_through_logging_config

from airflow_ext.wrapper import Airflow


def pass_through_cli() -> None:
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = Airflow()
    ext.pass_through_invoker(
        structlog.getLogger("airflow_invoker"),
        *sys.argv[1:] if len(sys.argv) > 1 else [],
    )
