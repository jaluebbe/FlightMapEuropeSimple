import json
import os
import pandas as pd
import redis

url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
data = pd.read_csv(url)

keys = ['date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
    'total_vaccinations']

world_data = data[data.iso_code == 'OWID_WRL'][keys]
covid_data = {'world': world_data.to_dict(orient='list')}
json_data = json.dumps(world_data.to_dict(orient='list')).replace(
    'NaN', 'null').replace('.0,', ',').replace('.0]', ']')

with open('static/covid_data.json', 'w') as f:
    f.write(json_data+'\n')

redis_connection = redis.Redis(os.getenv('REDIS_HOST'), decode_responses=True)
redis_connection.set('covid_data', json_data)
