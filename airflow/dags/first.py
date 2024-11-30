from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import requests
import logging
import random

quotes = ['What a good day to be alive!!', 'Expectations hurt!!', 'You are strong!!']

# Logging setup
logging.basicConfig(level=logging.INFO)

def print_welcome():
    logging.info('Welcome to Airflow!')

def print_date():
    logging.info('Today is {}'.format(datetime.today().date()))

def print_random_quote():
    quote = random.choice(quotes)
    logging.info(f'Your quote: {quote}')
    

dag = DAG(
    'welcome_dag',
    default_args={'start_date': days_ago(1)},
    schedule_interval='0 18 * * *',
    catchup=False
)

print_welcome_task = PythonOperator(
    task_id='print_welcome',
    python_callable=print_welcome,
    dag=dag
)

print_date_task = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    dag=dag
)

print_random_quote_task = PythonOperator(
    task_id='print_random_quote',
    python_callable=print_random_quote,
    dag=dag
)

# Set the dependencies between the tasks
print_welcome_task >> print_date_task >> print_random_quote_task
