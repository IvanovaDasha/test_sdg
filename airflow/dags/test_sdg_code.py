from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import pandas as pd




default_args = {
    'owner': 'IvanovaDasha',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def greet(some_dict, ti):

    df = pd.read_csv(r'dataset.csv')

    print("some dict: ", some_dict)
    first_name = ti.xcom_pull(task_ids='get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name', key='last_name')
    age = ti.xcom_pull(task_ids='get_age', key='age')
    print(f"Hello World! My name is {first_name} {last_name}, "
          f"and I am {age} years old!")


def get_name(ti):
    ti.xcom_push(key='first_name', value='Jerry')
    ti.xcom_push(key='last_name', value='Fridman')


def get_age(ti):
    ti.xcom_push(key='age', value=19)


with DAG(
    default_args=default_args,
    dag_id='a_sdg_test',
    description='Test SDG',
    start_date=datetime(2021, 10, 6),
    schedule_interval='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='load_data',
        python_callable=greet,
    )

    task2 = PythonOperator(
        task_id='model',
        python_callable=get_name
    )

    task3 = PythonOperator(
        task_id='test_model',
        python_callable=get_age
    )

    task1 >> task2 >> task3