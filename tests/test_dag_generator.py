"""Validate the Airflow DAG generator that `airflow_extension initialize` installs."""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING, Any

from airflow.models import DagBag

if TYPE_CHECKING:
    from collections.abc import Callable

SCHEDULES_V1 = [
    {
        "name": "legacy-schedule",
        "extractor": "tap-mock",
        "loader": "target-mock",
        "transform": "run",
        "interval": "@hourly",
        "cron_interval": "@hourly",
    },
]

SCHEDULES_V2 = {
    "schedules": {
        "elt": [
            {
                "name": "gitlab-to-postgres",
                "extractor": "tap-gitlab",
                "loader": "target-postgres",
                "transform": "run",
                "interval": "@daily",
                "cron_interval": "@daily",
            },
            {
                "name": "once-off",
                "extractor": "tap-mock",
                "loader": "target-mock",
                "transform": "skip",
                "interval": "@once",
                "cron_interval": None,
            },
        ],
        "job": [
            {
                "name": "daily-job",
                "cron_interval": "@daily",
                "job": {
                    "name": "my-job",
                    "tasks": ["tap-mock target-mock", ["dbt-mock:run"]],
                },
            },
        ],
    },
}


def _load_dag_bag() -> DagBag:
    """Process the packaged DAG generator file with an empty, non-scanning DagBag."""
    with importlib.resources.as_file(
        importlib.resources.files("airflow_ext.files").joinpath(
            "orchestrate",
            "meltano.py",
        ),
    ) as dag_generator_path:
        dagbag = DagBag(dag_folder=None, collect_dags=False)
        dagbag.process_file(str(dag_generator_path))
    return dagbag


def test_v1_schedules_produce_valid_dag(meltano_project: Callable[[Any], None]) -> None:
    """A legacy (v1) `meltano schedule list` export generates a DAG with no import errors."""
    meltano_project(SCHEDULES_V1)

    dagbag = _load_dag_bag()

    assert dagbag.import_errors == {}
    assert "meltano_legacy-schedule" in dagbag.dags
    assert dagbag.dags["meltano_legacy-schedule"].task_ids == ["extract_load"]


def test_v2_schedules_produce_valid_dags(meltano_project: Callable[[Any], None]) -> None:
    """A v2 `meltano schedule list` export generates DAGs for elt and job schedules."""
    meltano_project(SCHEDULES_V2)

    dagbag = _load_dag_bag()

    assert dagbag.import_errors == {}
    assert set(dagbag.dags) == {"meltano_gitlab-to-postgres", "meltano_daily-job_my-job"}

    elt_dag = dagbag.dags["meltano_gitlab-to-postgres"]
    assert elt_dag.task_ids == ["extract_load"]

    job_dag = dagbag.dags["meltano_daily-job_my-job"]
    assert job_dag.task_ids == ["meltano_daily-job_my-job_task0", "meltano_daily-job_my-job_task1"]
    task1 = job_dag.get_task("meltano_daily-job_my-job_task1")
    assert task1.upstream_task_ids == {"meltano_daily-job_my-job_task0"}


def test_once_off_schedule_is_skipped(meltano_project: Callable[[Any], None]) -> None:
    """Schedules with no cron interval (`@once`) are not turned into DAGs."""
    meltano_project(SCHEDULES_V2)

    dagbag = _load_dag_bag()

    assert "meltano_once-off" not in dagbag.dags


def test_empty_schedules_produce_no_dags(meltano_project: Callable[[Any], None]) -> None:
    """An empty schedule list is a valid, if unremarkable, Meltano project state."""
    meltano_project([])

    dagbag = _load_dag_bag()

    assert dagbag.import_errors == {}
    assert dagbag.dags == {}
