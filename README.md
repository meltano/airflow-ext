# ext-airflow
Meltano Airflow utility extension

## installation


```shell
# Install the extension
meltano add utility airflow
# seed the database, create default airflow.cfg, deploy the meltano dag orchestrator
meltano airflow initialize
# create a airflow user with admin privs
meltano invoke airflow invoke users create -u admin@localhost -p password --role Admin -e admin@localhost -f admin -l admin
# start the scheduler, backgrounding the process
meltano airflow scheduler & 
# start the webserver, keeping it in the foreground
meltano airflow webserver 
```

### example meltano.yml

```yaml
  utilities:
  - name: airflow
    namespace: airflow
    pip_url: git+https://github.com/meltano/ext-airflow.git@feat-init-extension apache-airflow==2.3.3 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.3.3/constraints-no-providers-${MELTANO__PYTHON_VERSION}.txt
    executable: airflow_extension
    env:
      AIRFLOW__WEBSERVER__WEB_SERVER_PORT: "8080"
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: "true"
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: "sqlite:///$MELTANO_PROJECT_ROOT/airflow/airflow.db"
      AIRFLOW__CORE__DAGS_FOLDER: "$MELTANO_PROJECT_ROOT/orchestrate/dags"
    config:
      home: $MELTANO_PROJECT_ROOT/airflow
      config: $MELTANO_PROJECT_ROOT/airflow/airflow.cfg
    commands:
      webserver: invoke webserver
      scheduler: invoke scheduler
      version: invoke version
environments:
- name: dev
- name: staging
- name: prod
```

## caveats