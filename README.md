# ext-airflow
Meltano Airflow utility extension

### example meltano.yml

```yaml
  utilities:
  - name: airflow
    namespace: airflow
    pip_url: git+https://github.com/meltano/ext-airflow.git@feat-init-extension apache-airflow==2.3.3
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
    - name: core.dags_folder
      label: DAGs Folder
      value: $MELTANO_PROJECT_ROOT/orchestrate/dags
      env: AIRFLOW__CORE__DAGS_FOLDER
    - name: core.plugins_folder
      label: Plugins Folder
      value: $MELTANO_PROJECT_ROOT/orchestrate/plugins
      env: AIRFLOW__CORE__PLUGINS_FOLDER
    - name: core.load_examples
      label: Load Examples
      value: false
      env: AIRFLOW__CORE__LOAD_EXAMPLES
    - name: core.dags_are_paused_at_creation
      label: Pause DAGs at Creation
      env: AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION
      value: false
    - name: database.sql_alchemy_conn
      label: SQL Alchemy Connection
      value: sqlite:///$MELTANO_PROJECT_ROOT/airflow/airflow.db
      env: AIRFLOW__CORE__SQL_ALCHEMY_CONN
    - name: webserver.web_server_port
      label: Webserver Port
      value: 8080
      env: AIRFLOW__WEBSERVER__WEB_SERVER_PORT
    config:
      home: $MELTANO_PROJECT_ROOT/airflow
      config: $MELTANO_PROJECT_ROOT/airflow/airflow.cfg
```

## installation

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

## Cookiecutter

```shell
# Create a new project
$ cookiecutter cookiecutter/wrapper-template -o path/to/your/project
source_name [MyExtensionName]: Airflow
admin_name [FirstName LastName]: Bob Loblaw
extension_name [airflow]:
wrapper_id [ext-airflow]:
library_name [ext_airflow]:
cli_prefix [airflow]:
wrapper_target_name [some-third-party-cli]: airflow
```

```shell
cd path/to/your/project
poetry install
poetry run airflow_extension describe
```