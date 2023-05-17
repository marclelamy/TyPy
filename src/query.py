import pandas as pd
import os
import time
from tabulate import tabulate


cwd = os.getcwd()

def query_table(con, table_name, condition=''): 
    query = f'''
    select 
        * 
    from {table_name} 
    where 1 = 1 
        {condition}'''
    
    return pd.read_sql_query(query, con)


def npast_games_words(con, n_past_games=1000000, n_past_words=1000000):
    '''Returns a list of words from the last n games played
    '''

    query_npast_games_words = f'''
        select
            game_id
            , sentence
            , datetime(max(time), 'unixepoch', 'localtime') time

        from keys_pressed 
        left join clean_games_settings using(game_id)
        group by 1, 2
        order by 3 desc
        limit {n_past_games}
        '''

    df_query = pd.read_sql_query(query_npast_games_words, con)
    print(' '.join(df_query['sentence'].unique()))
    done_words = ' '.join(df_query['sentence'].unique()).split(' ')[:n_past_words]

    return done_words



def load_query(con, query_name: str, text_only: bool = False) -> list:
    '''Opens a given text file name and execute the 
    query to return a pd.DataFrame
    
    Parameter
    ---------
    query_name str: name of the file name to run
    '''

    # Open file and get the query 
    with open(f'{cwd}/data/queries/{query_name}.sql') as file: 
        query = file.read()

    if text_only == False:
        return pd.read_sql_query(query, con)
    elif text_only == True:
        return query



def letters_ranking(con, n_games: int = 10, n_letters: int = 10): 
    new_query = '''
    with tbl as (
    select 
        key
        , time
        , lead(time) over(partition by game_id order by time desc) lead_time
        , time - lead(time) over(partition by game_id order by time desc) time_diff
        --, lead(key) over(order by time desc) lead_key
        --, lead(time) over(order by time desc) lead_time
        , row_number() over(partition by key order by time desc) rank

    from keys_pressed
    left join clean_games_settings using(game_id)
    where 1=1 
        and word_count > 20
        and correct_key = 1

    order by time 
    )


    select 
        key
        , avg(time_diff) time_diff

    from tbl 
    where rank <= 200

    group by 1
    order by 2 desc

    '''

    df = pd.read_sql_query(new_query, con).sort_values('time_diff')
    print(tabulate(df))