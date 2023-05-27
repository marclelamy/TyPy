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


def npast_games_words(con, n_past_games=None):
    '''Returns a list of words from the last n games played
    '''
    if n_past_games == None:
        n_past_games = 1000000

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
    ngames_past_words = ' '.join(df_query['sentence'].unique()).split(' ')
    return ngames_past_words



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



def character_ranking(con, max_key_count_to_use=None, min_key_count_to_use=None, condition='', order='desc'): 
    '''Returns a dataframe with the ranking of the characters
    based on the time it takes to type them.
    '''
    if max_key_count_to_use == None:
        max_key_count_to_use = 1_000_000
    if min_key_count_to_use == None:
        min_key_count_to_use = 0

    query = f''' 
    with time_per_key as (
    select 
        key
        , time
        , lead(time) over(partition by game_id order by time desc) lead_time
        , time - lead(time) over(partition by game_id order by time desc) time_diff
        --, lead(key) over(order by time desc) lead_key
        --, lead(time) over(order by time desc) lead_time
        , row_number() over(partition by key order by time desc) letter_descending_rank 

    from keys_pressed
    left join clean_games_settings using(game_id)
    where 1=1 
        --and word_count > 20
        and correct_key = 1

    order by time 
    )


    select 
        key 
        , avg(time_diff) avg_time_diff
        , round(avg(time_diff) - lag(avg(time_diff)) over(order by avg(time_diff)), 4) diff
        , count(*) count
        , c.type

    from time_per_key tpk
    left join characters c on tpk.key = c.character
    where 1=1
        and letter_descending_rank <= {max_key_count_to_use}
        and letter_descending_rank >= {min_key_count_to_use}
        {condition}
            
    group by key
    order by avg_time_diff {order}
    '''

    df  = pd.read_sql_query(query, con)
    df['time_diff'] = df['diff'].expanding().sum()
    return df 