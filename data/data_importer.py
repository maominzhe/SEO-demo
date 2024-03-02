import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

db_config = {
    'dbname': 'zalando',
    'user': 'postgres',
    'password': '101701',
    'host': 'localhost'
}

engine = create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["dbname"]}')

csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]


for file in csv_files:
    table_name = file[:-4]
    file_path = os.path.join('data', file)
    df = pd.read_csv(file_path)

    df.to_sql(table_name, engine, if_exists='replace', index=False)

    print(f'{file} hass been imported into {table_name} table.')