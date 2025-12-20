



import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from score import Score
import os 
from tabulate import tabulate

current_dir = os.getcwd()
con = sqlite3.connect("data/main_database.db")
# pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.max_columns', None)
connew = sqlite3.connect("data/main_database_new.db")

from tqdm import tqdm

import os

# Directory to start the search
directory = os.getcwd()

database_paths = []
# Loop through all the directories and files starting from the given directory
for root, dirs, files in os.walk(directory):
    # Loop through all the files in the current directory
    for filename in files:
        # Print the full path to the file
        file_path = os.path.join(root, filename)
        print(file_path)

        if file_path.endswith('.db'):
            database_paths.append(file_path)





def concat_sqlite_databases(databases, output_path):
    """
    Concatenate tables from SQLite databases with the same table and column names
    and write the result to a new SQLite database.

    Args:
        databases (list of str): Paths to the input SQLite databases.
        output_path (str): Path to the output SQLite database.

    Returns:
        None.
    """

    # Create a connection to the output database
    output_conn = sqlite3.connect(output_path)

    # Loop through each input database
    for db_path in tqdm(databases):
        try: 
            # Create a connection to the input database
            input_conn = sqlite3.connect(db_path)

            # Get a list of the table names in the input database
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", input_conn)['name'].tolist()

            # Loop through each table in the input database
            for table_name in tqdm(tables):
                # Read the current table from the input database into a DataFrame
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", input_conn)

                # Check if a table with the same name already exists in the output database
                table_exists = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'", output_conn)

                # If the table doesn't exist, write the DataFrame to a new table in the output database
                if table_exists.empty:
                    df.to_sql(table_name, output_conn)

                # If the table already exists, check if the column names are the same
                else:
                    existing_cols = pd.read_sql_query(f"PRAGMA table_info({table_name})", output_conn)['name']
                    new_cols = df.columns
                    # If the column names are the same, concatenate the new data with the existing data in the output database
                    existing_data = pd.read_sql_query(f"SELECT * FROM {table_name}", output_conn)
                    concatenated_data = pd.concat([existing_data, df], axis=0)
                    print(concatenated_data.shape, concatenated_data.drop_duplicates().shape)
                    concatenated_data.drop_duplicates().to_sql(table_name, output_conn, if_exists='replace', index=False)

            # Close the connection to the input database
            input_conn.close()

        except:
            print(f"Error: {db_path} is not a valid database")

    # Close the connection to the output database
    output_conn.close()




concat_sqlite_databases(database_paths, 'data/main_database.db')