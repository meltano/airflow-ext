# airflow-ext

Meltano Airflow utility extension

## Example meltano.yml entry

```yaml
  utilities:
  - name: airflow
    namespace: airflow
    pip_url: git+https://github.com/meltano/airflow-ext.git@main apache-airflow==2.3.3
      --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.3.3/constraints-no-providers-3.8.txt
    executable: airflow_invoker
    commands:
      describe:
        executable: airflow_extension
        args: describe
      initialize:
        executable: airflow_extension
        args: initialize
      invoke:
        executable: airflow_extension
        args: invoke
    settings:
    - name: database.sql_alchemy_conn
      label: SQL Alchemy Connection
      value: sqlite:///$MELTANO_PROJECT_ROOT/.meltano/utilities/airflow/airflow.db
      env: AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
    - name: core.dags_folder
      label: DAGs Folder
      value: $MELTANO_PROJECT_ROOT/orchestrate/airflow/dags
      env: AIRFLOW__CORE__DAGS_FOLDER
    - name: core.plugins_folder
      label: Plugins Folder
      value: $MELTANO_PROJECT_ROOT/orchestrate/airflow/plugins
      env: AIRFLOW__CORE__PLUGINS_FOLDER
    - name: core.load_examples
      label: Load Examples
      value: false
      env: AIRFLOW__CORE__LOAD_EXAMPLES
    - name: core.dags_are_paused_at_creation
      label: Pause DAGs at Creation
      env: AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION
      value: false
    - name: webserver.web_server_port
      label: Webserver Port
      value: 8080
      env: AIRFLOW__WEBSERVER__WEB_SERVER_PORT
    - name: logging.base_log_folder
      label: Base Log Folder
      value: $MELTANO_PROJECT_ROOT/.meltano/utilities/airflow/logs
      env: AIRFLOW__LOGGING__BASE_LOG_FOLDER
      description: |
        The folder where airflow should store its log files. This path must be absolute. There are a few existing
        configurations that assume this is set to the default. If you choose to override this you may need to update
        the dag_processor_manager_log_location and child_process_log_directory settings as well.
    - name: logging.dag_processor_manager_log_location
      label: Dag Processor Manager Log Location
      value: $MELTANO_PROJECT_ROOT/.meltano/utilities/airflow/logs/dag_processor_manager/dag_processor_manager.log
      env: AIRFLOW__LOGGING__DAG_PROCESSOR_MANAGER_LOG_LOCATION
      description: |
        Where to send dag parser logs.
    - name: scheduler.child_process_log_directory
      label: Child Process Log Directory
      value: $MELTANO_PROJECT_ROOT/.meltano/utilities/airflow/logs/scheduler
      env: AIRFLOW__SCHEDULER__CHILD_PROCESS_LOG_DIRECTORY
      description: |
        Where to send the logs of each scheduler process.
    - name: extension.airflow_home
      label: Airflow Home
      value: $MELTANO_PROJECT_ROOT/orchestrate/airflow
      env: AIRFLOW_HOME
      description: |
        The directory where Airflow will store its configuration, logs, and other files.
    - name: extension.airflow_config
      label: Airflow Home
      value: $MELTANO_PROJECT_ROOT/orchestrate/airflow/airflow.cfg
      env: AIRFLOW_CONFIG
      description: |
        The path where the Airflow configuration file will be stored.
```

## Installation

```shell
# Install the extension
meltano install utility airflow

# explicitly seed the database, create default airflow.cfg, deploy the meltano dag orchestrator
meltano invoke airflow:initialize

# verify that airflow can be called via the extensions invoker
meltano invoke airflow version
# see what other commands are available
meltano invoke airflow --help

# create a airflow user with admin privs
meltano invoke airflow users create -u admin@localhost -p password --role Admin -e admin@localhost -f admin -l admin

# start the scheduler, backgrounding the process
meltano invoke airflow scheduler &
# start the webserver, keeping it in the foreground
meltano invoke airflow webserver
```
