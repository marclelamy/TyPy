import pandas as pd 
import plotly.express as px



def load_games_summary(con): 
    query = '''
    select 
        * 
    from games_summary
    '''

    return pd.read_sql(query, con)


def load_keys_pressed(con): 
    query = '''
    select 
        * 
    from keys_pressed
    '''

    return pd.read_sql(query, con)

def load_table(con, table_name): 
    query = f'''
    select 
        * 
    from {table_name}
    '''

    return pd.read_sql(query, con)