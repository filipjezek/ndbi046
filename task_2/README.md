# Data cube assignment

## System requirements

- docker (with at least 4GB of allocated memory)

## Installation & running

1. `docker compose up --build`
2. open <localhost:8080>
3. username: `airflow`, password: `airflow`
4. find the `data_cubes` DAG, run it with configuration
   - there is a mandatory `output_path` arg (for example `{"output_path": "/opt/airflow/dags/"}`)

## Scripts

Scripts are pretty much unchanged from `task_1`

## Airflow configuration

The docker files were taken from [docs](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).
DAG configuration can be found in `./airflow/dags/cubes_dag.py`.
