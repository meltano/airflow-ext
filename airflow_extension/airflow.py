from __future__ import annotations

import pkgutil
import os
import subprocess
import sys
from pathlib import Path

import structlog

from meltano_extension_sdk.extension import Description, ExtensionBase
from meltano_extension_sdk.process import Invoker, log_subprocess_error

log = structlog.get_logger()


class Airflow(ExtensionBase):
    def __init__(self):

        self.app_name = "airflow_extension"
        self.airflow_bin = "airflow"
        self.airflow_invoker = Invoker(self.airflow_bin, env=os.environ.copy())

        self.airflow_home = os.environ.get("AIRFLOW_HOME") or os.environ.get(
            f"{self.app_name}_AIRFLOW_HOME"
        )
        if not self.airflow_home:
            log.debug("env dump", env=os.environ)
            log.error(
                "AIRFLOW_HOME not found in environment, unable to function without it"
            )
            sys.exit(1)

        self.airflow_cfg_path = Path(os.environ.get("AIRFLOW_CONFIG", f"{self.airflow_home}/airflow.cfg"))
        if not self.airflow_cfg_path:
            log.debug("env dump", env=os.environ)
            log.error(
                "AIRFLOW_CONFIG not found in environment, unable to function without it"
            )
            sys.exit(1)
        if not self.airflow_cfg_path.exists():
            log.warning(
                "airflow.cfg does not exist, will be auto-generated with defaults",
                airflow_cfg_path=self.airflow_cfg_path,
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

    def pre_invoke(self):
        self._create_config()
        self._initdb()

    def initialize(self, force: bool = False):
        self.pre_invoke()

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

    def invoke(self, command_name: str | None, *command_args):
        try:
            self.airflow_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"airflow {command_name}", err, "airflow invocation failed"
            )
            sys.exit(1)

    def describe(self) -> Description:
        # TODO: could we build this from typer instead?
        return Description(commands=[":splat", "webserver", "scheduler", "version"])

    def _create_config(self):
        # create an initial airflow config file
        try:
            self.airflow_invoker.run("--help", stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                "airflow --help", err, "initial airflow invocation failed"
            )
            sys.exit(1)

    def _initdb(self):
        """Initialize the airflow metadata database."""
        try:
            self.airflow_invoker.run("db", "init")
        except subprocess.CalledProcessError as err:
            log_subprocess_error("airflow db init", err, "airflow db init failed")
            sys.exit(1)
