import os
import sys

import structlog

from ext_airflow.airflow import Airflow
from meltano_extension_sdk.logging import pass_through_logging_config


def pass_through_cli():
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = Airflow()
    ext.pass_through_invoker(
        structlog.getLogger("airflow_invoker"), *sys.argv[1:] if len(sys.argv) > 1 else []
    )
