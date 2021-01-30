import json
import os
import pandas as pd
import redis
import requests

url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
data = pd.read_csv(url)

keys = ['date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
    'total_vaccinations']

world_data = data[data.iso_code == 'OWID_WRL'][keys]
covid_data = {'world': world_data.to_dict(orient='list')}
json_data = json.dumps(world_data.to_dict(orient='list')).replace(
    'NaN', 'null').replace('.0,', ',').replace('.0]', ']')

redis_connection = redis.Redis(os.getenv('REDIS_HOST'), decode_responses=True)
redis_connection.set('covid_data', json_data)

statistics_url = os.getenv('STATISTICS_URL')
if statistics_url is None:
    statistics_url = 'https://jaluebbe.github.io/FlightMapEuropeSimple/static'

_response = requests.get(statistics_url+'/flights_statistics.json')
if _response.status_code == 200:
    redis_connection.set('flights_statistics', _response.text)

_response = requests.get(statistics_url+'/fir_uir_statistics.json')
if _response.status_code == 200:
    redis_connection.set('fir_uir_statistics', _response.text)
