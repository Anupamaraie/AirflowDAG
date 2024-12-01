from airflow import DAG
from airflow.operators.python import PythonOperator

from bs4 import BeautifulSoup
import datetime as dt
import logging
import pandas as pd
from pydantic import BaseModel, ValidationError
import requests
from typing import List, Optional

# Pydantic models for college details
class College(BaseModel):
    name: str
    affiliation: Optional[str] = None # optional since they may not always exist
    address: Optional[str] = None 

def extract():
    colleges_list = []
    url = requests.get('https://edusanjal.com/college')
    # Checking if the url was successful or not
    if url.status_code != 200:
        raise Exception("Failed to load the page!")
    
    html_content = BeautifulSoup(url.content, "html.parser")
    # Finding college div
    container = html_content.find('div', class_='container')

    if not container:
        raise Exception("No container found")

    main = container.find_all('div')
    colleges = main[1].find_all('div')
    # Initializing a dictionary to store college information
    college_info = {}
    # Iterating through the list of colleges
    for college in colleges:
        names = college.find('a')  # find the first <a> tag (college name)
        details = college.find_all('li')  # find all <li> tags (details)
        if names and names.text.strip():
            college_name = names.text.strip()
            detail_texts = [detail.text.strip() for detail in details]
            try:
                # Creating and Validating the College Model using Pydantic
                college_data = College (
                    name = college_name,
                    affiliation=detail_texts[0] if len(detail_texts) > 0 else None,
                    address=detail_texts[1] if len(detail_texts) > 1 else None,
                )
                # Storing the validated college data
                colleges_list.append(dict(college_data))
        
            except ValidationError as e:
                print(f"Validation error for {college_name}: {e}")
                continue
    college_pd = pd.DataFrame(colleges_list)
    college_pd.to_csv('colleges.csv', index=False)
    logging.info('Data successfully extracted!')

def transform():
    
    df = pd.read_csv('colleges.csv')
    replacements = {
        'Tribhuvan University': 'TU',
        'National Examinations Board': 'NEB',
        'Pokhara University':'PU'
    }
    print(df.columns)
    df['affiliation'] = df['affiliation'].replace(replacements, regex=True)
    df[['location', 'city']] = df['address'].str.rsplit(',', n=1, expand=True)
    df.drop('address', axis=1, inplace=True)
    
    df.to_csv('transformed_collegedata.csv')
    logging.info('Data successfully transformed!')


def load():
    df = pd.read_csv('transformed_collegedata.csv')
    print(df)
    logging.info('Data loaded to csv successfully!')


dag = DAG(
    'collegeinfo_dag',
    default_args={'start_date': dt.datetime(2024,11,25)},
    # schedule_interval='0 20 * * *',
    schedule_interval=None, #trigger manually
    catchup=False
)

extract_task = PythonOperator(
    task_id = 'extract',
    python_callable=extract,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag
)

extract_task >> transform_task >> load_task