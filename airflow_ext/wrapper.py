"""Meltano Airflow extension."""
from __future__ import annotations

import os
import pkgutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error

log = structlog.get_logger("airflow_extension")


class Airflow(ExtensionBase):
    """Airflow extension implementing the ExtensionBase interface."""

    def __init__(self) -> None:
        """Initialize the airflow extension."""
        self.app_name = "airflow_extension"
        self.airflow_bin = "airflow"
        self.airflow_invoker = Invoker(self.airflow_bin)

        self.airflow_home = os.environ.get("AIRFLOW_HOME") or os.environ.get(
            f"{self.app_name}_AIRFLOW_HOME"
        )
        if not self.airflow_home:
            log.debug("env dump", env=os.environ)
            log.error(
                "AIRFLOW_HOME not found in environment, unable to function without it"
            )
            sys.exit(1)

        self.airflow_cfg_path = Path(
            os.environ.get("AIRFLOW_CONFIG", f"{self.airflow_home}/config/airflow.cfg")
        )
        self.airflow_core_dags_path = Path(
            os.path.expandvars(
                os.environ.get(
                    "AIRFLOW__CORE__DAGS_FOLDER",
                    f"{self.airflow_home}/orchestrate/dags",
                )
            )
        )
        # Configure the env to make airflow installable without GPL deps.
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"

    def pre_invoke(self, command_name: str | None, *command_args: Any) -> None:
        """Perform pre-invoke tasks for the extension.

        Args:
            command_name: The name of the command that will be invoked (unused).
            *command_args: The arguments that would be passed (unused).
        """
        self._create_config()
        self._initdb()

    def initialize(self, force: bool = False) -> None:
        """Initialize the extension.

        Args:
            force: If True, force initialization where possible (currently no where).
        """
        self.pre_invoke("initialize", None)

        self.airflow_core_dags_path.mkdir(parents=True, exist_ok=True)

        dag_generator_path = self.airflow_core_dags_path / "meltano_dag_generator.py"
        if not dag_generator_path.exists():
            log.warning(
                "meltano dag generator not found, will be auto-generated",
                dag_generator_path=dag_generator_path,
            )
            dag_generator_path.write_bytes(
                pkgutil.get_data("files_airflow_ext", "orchestrate/meltano.py")
            )

        readme_path = self.airflow_core_dags_path / "README.md"
        if not readme_path.exists():
            log.debug(
                "meltano dag generator README not found, will be auto-generated",
                readme_path=readme_path,
            )
            readme_path.write_bytes(
                pkgutil.get_data("files_airflow_ext", "orchestrate/README.md")
            )

        git_ignore_path = Path(self.airflow_home) / ".gitignore"
        if not git_ignore_path.exists():
            log.debug(
                "No .gitignore not found in $AIRFLOW_HOME, will be auto-generated",
                git_ignore_path=git_ignore_path,
                airflow_home=self.airflow_home,
            )
            git_ignore_path.write_bytes(
                pkgutil.get_data("files_airflow_ext", "dot-gitignore")
            )

    def invoke(self, command_name: str | None, *command_args: Any) -> None:
        """Invoke the airflow command.

        Note: will sys.exit() if the command fails.

        Args:
            command_name: The command name to invoke.
            command_args: The command args to pass along.
        """
        try:
            self.airflow_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"airflow {command_name}", err, "airflow invocation failed"
            )
            sys.exit(err.returncode)

    def describe(self) -> models.Describe:
        """Describe the extension.

        Returns:
            The extension description
        """
        # TODO: could we auto-generate all or portions of this from typer instead?
        return models.Describe(
            commands=[
                models.ExtensionCommand(
                    name="airflow_extension", description="airflow extension commands"
                ),
                models.InvokerCommand(
                    name="airflow_invoker", description="airflow pass through invoker"
                ),
            ]
        )

    def _create_config(self) -> None:
        self.airflow_cfg_path.parent.mkdir(parents=True, exist_ok=True)

        # create an initial airflow config file
        try:
            self.airflow_invoker.run("--help", stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                "airflow --help", err, "initial airflow invocation failed"
            )
            sys.exit(err.returncode)

    def _initdb(self) -> None:
        """Initialize the airflow metadata database."""
        try:
            self.airflow_invoker.run("db", "init")
        except subprocess.CalledProcessError as err:
            log_subprocess_error("airflow db init", err, "airflow db init failed")
            sys.exit(err.returncode)
