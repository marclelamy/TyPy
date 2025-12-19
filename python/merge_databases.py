import os 
import pandas as pd
import sqlite3
from tqdm import tqdm

allowed_extensions = ['db', 'sqlite', 'sqlite3']
parent_path = 'data/databases_archives/'
data = {}
for db_name in tqdm(os.listdir(parent_path)): 
    df_sqlite_master = pd.DataFrame()
    if db_name.split('.')[-1] not in allowed_extensions:
        continue 

    db_path = parent_path + db_name
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query('select * from sqlite_master', con)
    df_sqlite_master = pd.concat([df_sqlite_master, df], axis=0)

    for table_name in df_sqlite_master['name']: 
        if table_name not in data.keys(): 
            data[table_name] = pd.read_sql_query('select * from ' + table_name, con)
        else: 
            data[table_name] = pd.concat([data[table_name], pd.read_sql_query('select * from ' + table_name, con)], axis=0)


con_archive = sqlite3.connect('data/archive_database.sqlite')
for table_name in data.keys():
    df = data[table_name].drop_duplicates()
    df.to_sql(table_name, con_archive, if_exists='replace', index=False)
    print(table_name, df.shape)