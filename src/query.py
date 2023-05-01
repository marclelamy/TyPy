import pandas as pd
import os
import time


cwd = os.getcwd()

def query_table(con, table_name, condition): 
    query = f'''
    select 
        * 
    from {table_name} 
    where 1 = 1 
        {condition}'''
    
    return pd.read_sql_query(query, con)


def npast_games_words(con, n_past_games, corpus_size):
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
    done_words = ' '.join(df_query['sentence'].unique()).split(' ')

    # if len(set(done_words)) < corpus_size:
        

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



