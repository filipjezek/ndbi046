#!/usr/bin/env python3

import requests
from io import TextIOWrapper
from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator

import cube_scripts.care_providers
import cube_scripts.population


def fetch_data(url: str, dest: str, ssl=True):
    with requests.get(url, stream=True, verify=ssl) as stream:
        stream.raise_for_status()
        with open(dest, 'wb') as handle:
            for chunk in stream.iter_lines(1024 * 5):
                handle.write(chunk)


def transform_data(src_path: str, dest_filename: str, transform, *args, **kwargs):
    with open(src_path, 'r', encoding='UTF-8') as src:
        data_cube = transform(src, *args)
        output_path = Path(kwargs['dag_run'].conf.get(
            "output_path", None)) / dest_filename
        with open(str(output_path), 'wb') as dest:
            data_cube.serialize(
                format='ttl', encoding='UTF-8', destination=dest)


dag_args = {
    'email': ['filip.jezek@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=15)
}

with DAG(
    dag_id='data_cubes',
    default_args=dag_args,
    start_date=datetime(2023, 3, 27),
    schedule=None,
    catchup=False,
    tags=['NDBI046'],
) as dag:

    # providers

    prov_data_path = './dags/providers_data'
    prov_cube_filename = 'health_care.ttl'

    fetch_care_providers = PythonOperator(
        task_id='fetch_care_providers',
        python_callable=fetch_data,
        op_args=[
            'https://opendata.mzcr.cz/data/nrpzs/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv',
            prov_data_path
        ]
    )
    fetch_care_providers.doc_md = '''\
    downloads the care providers dataset
    '''

    transform_care_providers = PythonOperator(
        task_id='transform_care_providers',
        python_callable=transform_data,
        op_args=[
            prov_data_path,
            prov_cube_filename,
            cube_scripts.care_providers.create_cube
        ]
    )
    transform_care_providers.doc_md = '''\
    Converts the care providers csv to a data cube RDF Turtle file. Uses the `output_path` dag run arg.
    '''

    # population

    pop_data_path = './dags/population_data'
    pop_counties_path = './dags/counties'
    pop_cube_filename = 'population.ttl'

    fetch_population = PythonOperator(
        task_id='fetch_population',
        python_callable=fetch_data,
        op_args=[
            'https://www.czso.cz/documents/10180/184344914/130141-22data2021.csv',
            pop_data_path
        ]
    )
    fetch_population.doc_md = '''\
    downloads the population dataset
    '''

    fetch_counties = PythonOperator(
        task_id='fetch_counties',
        python_callable=fetch_data,
        op_args=[
            'https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/02/číselník-okresů-vazba-101-nadřízený.csv',
            pop_counties_path,
            False
        ]
    )
    fetch_counties.doc_md = '''\
    downloads the county codes data
    '''

    transform_population = PythonOperator(
        task_id='transform_population',
        python_callable=transform_data,
        op_args=[
            pop_data_path,
            pop_cube_filename,
            cube_scripts.population.create_cube,
            pop_counties_path
        ]
    )
    transform_population.doc_md = '''\
     Converts the population csv to a data cube RDF Turtle file. Uses the `output_path` dag run arg.
     '''

    fetch_care_providers >> transform_care_providers
    [fetch_population, fetch_counties] >> transform_population
