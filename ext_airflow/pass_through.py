import sys

import structlog

from ext_airflow.airflow import Airflow


def pass_through_cli():
    """Pass through CLI entry point."""
    ext = Airflow()
    ext.pass_through_invoker(
        structlog.getLogger("airflow_invoker"), sys.argv[1], *sys.argv[2:]
    )
