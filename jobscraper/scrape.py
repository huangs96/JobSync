import asyncio
import psycopg2
import tracemalloc
import time as tm
import yaml
import httpx
import sqlite3
from http.client import HTTPException
from re import search
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime, timedelta, time
from itertools import groupby
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from django.db import connections


# Trace memory usage and allocation
tracemalloc.start()

def load_config(config_file):
    with open(config_file, 'r') as stream:
        return yaml.safe_load(stream)

async def check_for_table(connection_alias, table_name):
  try:
    connection = connections[connection_alias]
    with connection.cursor() as cursor:
      cursor.execute(f"SELECT to_regclass('public.{table_name}')")
      return cursor.fetchone()[0] is not None
  except Exception as e:
    return False

async def create_table_if_not_exists_sqlite(config, db_path):
  connection = sqlite3.connect(db_path)
  cursor = connection.cursor()
  cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {config['jobs_tablename']} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      company TEXT,
      location TEXT,
      date_posted DATE,
      date_applied DATE,
      job_url TEXT,
      job_description TEXT,
      application_status TEXT
    )
  """)
  connection.commit()
  cursor.close()

async def save_jobs_to_database(jobs, config):
  database_type = config['db_type']
  if database_type == 'postgres':
    connection = psycopg2.connect(
        database="job_apps",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )
  elif database_type == 'sqlite':
    connection = sqlite3.connect(config['db_path'])
  else:
    raise ValueError("Database type currently not supported")

  cursor = connection.cursor()

  for job in jobs:
    if database_type == 'postgres':
      query = f"""
          INSERT INTO job_applications_jobapplication (title, company, location, date_posted, job_url, job_description)
          VALUES (%s, %s, %s, %s, %s, %s)
      """
    elif database_type == 'sqlite':
      query = """
              INSERT INTO job_applications_jobapplication (title, company, location, date_posted, date_applied, job_url, job_description, application_status)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          """
    
    date_posted = job.get('date')
    date_applied = job.get('date_applied', datetime.now().date())

    if date_posted is not None:
        values = (job['title'], job['company'], job['location'], date_posted, job['job_url'], job['job_description'], date_applied)
    else:
        date_default = datetime.now().date()
        values = (job['title'], job['company'], job['location'], date_default, job['job_url'], job['job_description'], date_applied)
    
    cursor.execute(query, values)

  connection.commit()
  cursor.close()
  connection.close()

async def getWithRetries(url, config, retries=3, delay=1):
    for i in range(retries):
        try:
            if len(config['proxies']) > 0:
                async with httpx.AsyncClient(proxies={'http://':config['proxies']['http']}) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        unparsedJobList = BeautifulSoup(response.content, 'html.parser')
                        return unparsedJobList
        except Exception as e:
            print(f"no proxy: {e}")

async def parseJobList(content):
    joblist = []
    try:
        divs = content.find_all('div', class_='base-search-card__info')
    except:
        print("No Jobs Found")
        return joblist
    for listing in divs:
        title = listing.find('h3').text.strip()
        company = listing.find('a', class_='hidden-nested-link')
        location = listing.find('span', class_='job-search-card__location')
        parent_div = listing.parent
        entity_urn = parent_div['data-entity-urn']
        job_posting_id = entity_urn.split(':')[-1]
        job_url = 'https://www.linkedin.com/jobs/view/'+job_posting_id+'/'
        date_tag_new = listing.find('time', class_ = 'job-search-card__listdate--new')
        date_tag = listing.find('time', class_='job-search-card__listdate')
        date = date_tag['datetime'] if date_tag else date_tag_new['datetime'] if date_tag_new else ''
        job_description = ''
        job = {
            'title': title,
            'company': company.text.strip().replace('\n', ' ') if company else '',
            'location': location.text.strip() if location else '',
            'date': date,
            'job_url': job_url,
            'job_description': job_description,
            'applied': 0,
            'hidden': 0,
            'interview': 0,
            'rejected': 0
        }
        joblist.append(job)
    return joblist

async def transform_job(content):
    div = content.find('div', class_='description__text description__text--rich')
    if div:
        # Remove unwanted elements
        for element in div.find_all(['span', 'a']):
            element.decompose()

        # Replace bullet points
        for ul in div.find_all('ul'):
            for li in ul.find_all('li'):
                li.insert(0, '-')

        text = div.get_text(separator='\n').strip()
        text = text.replace('\n\n', '')
        text = text.replace('::marker', '-')
        text = text.replace('-\n', '- ')
        text = text.replace('Show less', '').replace('Show more', '')
        return text
    else:
        return "Could not find Job Description"

def remove_irrelevant_jobs(joblist, config):
    #Filter out jobs based on description, title, and language. Set up in config.json.
    new_joblist = [job for job in joblist if not any(word.lower() in job['job_description'].lower() for word in config['desc_words'])]   
    new_joblist = [job for job in new_joblist if not any(word.lower() in job['title'].lower() for word in config['title_exclude'])] if len(config['title_exclude']) > 0 else new_joblist
    new_joblist = [job for job in new_joblist if any(word.lower() in job['title'].lower() for word in config['title_include'])] if len(config['title_include']) > 0 else new_joblist
    new_joblist = [job for job in new_joblist if safe_detect(job['job_description']) in config['languages']] if len(config['languages']) > 0 else new_joblist
    new_joblist = [job for job in new_joblist if not any(word.lower() in job['company'].lower() for word in config['company_exclude'])] if len(config['company_exclude']) > 0 else new_joblist

    return new_joblist

def remove_duplicates(joblist, config):
    # Remove duplicate jobs in the joblist. Duplicate is defined as having the same title and company.
    joblist.sort(key=lambda x: (x['title'], x['company']))
    joblist = [next(g) for k, g in groupby(joblist, key=lambda x: (x['title'], x['company']))]
    return joblist

def convert_date_format(date_string):
    """
    Converts a date string to a date object. 
    
    Args:
        date_string (str): The date in string format.

    Returns:
        date: The converted date object, or None if conversion failed.
    """
    date_format = "%Y-%m-%d"
    try:
        job_date = datetime.strptime(date_string, date_format).date()
        return job_date
    except ValueError:
        print(f"Error: The date for job {date_string} - is not in the correct format.")
        return None

def safe_detect(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'en'

# REPLACE WITH CURRENT DATABASE INFORMATION
def find_new_jobs(all_jobs, conn, config):
    # From all_jobs, find the jobs that are not already in the database. Function checks both the jobs and filtered_jobs tables.
    jobs_tablename = config['jobs_tablename']
    filtered_jobs_tablename = config['filtered_jobs_tablename']
    jobs_db = pd.DataFrame()
    filtered_jobs_db = pd.DataFrame()    
    if conn is not None:
        if table_exists(conn, jobs_tablename):
            query = f"SELECT * FROM {jobs_tablename}"
            jobs_db = pd.read_sql_query(query, conn)
        if table_exists(conn, filtered_jobs_tablename):
            query = f"SELECT * FROM {filtered_jobs_tablename}"
            filtered_jobs_db = pd.read_sql_query(query, conn)

    new_joblist = [job for job in all_jobs if not job_exists(jobs_db, job) and not job_exists(filtered_jobs_db, job)]
    return new_joblist

async def scrape():
  start_time = tm.perf_counter()
  finalJobList = []

  config = load_config('/Users/stephenhuang/TheWork/JobSync/config.yml')
  searchQueries = config['search_queries']
  for query in searchQueries:
    keywords = quote(query['keywords'])
    location = quote(query['location'])
    
    for i in range(0, config['pages_to_scrape']):
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&f_TPR=&f_WT={query['f_WT']}&geoId=&f_TPR={config['timespan']}&start={25*i}"
        result = await getWithRetries(url, config)
        parsedResult = await parseJobList(result)
        
        await save_jobs_to_database(parsedResult, config)
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage: {current / 10**6} MB")
        print(f"Peak memory usage: {peak / 10**6} MB")
        end_time = tm.perf_counter()
        print(f"Scraping finished in {end_time - start_time:.2f} seconds")
  tracemalloc.stop()
        

asyncio.run(scrape())