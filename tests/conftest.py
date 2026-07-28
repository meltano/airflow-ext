"""Shared fixtures for validating the generated Airflow DAG file."""

from __future__ import annotations

import importlib.metadata
import json
import os
import stat
import sys
import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

AIRFLOW_VERSION = importlib.metadata.version("apache-airflow")


def pytest_report_header(config: pytest.Config) -> list[str]:
    """Return a list of strings to be displayed in the header of the report."""
    return [
        f"Airflow: {AIRFLOW_VERSION}",
    ]


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest."""
    if AIRFLOW_VERSION.startswith("2"):
        config.addinivalue_line("filterwarnings", "once::airflow.exceptions.RemovedInAirflow3Warning")


@pytest.fixture
def meltano_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[[Any], None]:
    """Stub Meltano project whose `meltano schedule list` output can be set per-test.

    Returns a callable that writes a fake `meltano` executable onto PATH which prints
    the given schedule payload as JSON, mimicking `meltano schedule list --format=json`.
    """
    monkeypatch.setenv("AIRFLOW_HOME", str(tmp_path / "airflow_home"))

    project_root = tmp_path / "project"
    bin_dir = project_root / "bin"
    bin_dir.mkdir(parents=True)
    monkeypatch.setenv("MELTANO_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")

    def _stub_schedule_list(schedule_payload: list[dict] | dict) -> None:
        meltano_stub = bin_dir / "meltano"
        script = textwrap.dedent(f"""\
            #!{sys.executable}
            import sys
            sys.stdout.write({json.dumps(schedule_payload)!r})
            """)
        meltano_stub.write_text(script)
        meltano_stub.chmod(meltano_stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    return _stub_schedule_list
