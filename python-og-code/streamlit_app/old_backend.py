# import streamlit as st 
import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px


# con = sqlite3.connect('data/main_database.sqlite')
# con = sqlite3.connect('data/main_database.sqlite')
def query_table(con, table_name, condition=''): 
    query = f'''
    select 
        * 
    from {table_name} 
    where 1 = 1 
        {condition}'''
    return pd.read_sql_query(query, con)

def time_played(con) -> int:
    query = '''
            select 
                game_id
                , max(time) - min(time) game_duration
            
            from keys_pressed
            group by 1
            '''

    df = pd.read_sql_query(query, con)
    total_time_played = df['game_duration'].sum()
    return round(total_time_played)


def load_game_settings(con): 
    query = '''
            select 
                *

            from clean_games_settings
            '''

    df = pd.read_sql_query(query, con)
    return df


def list_players(con) -> int:
    query = '''
            select 
                distinct 
                player_name
            from clean_games_settings
            '''

    df = pd.read_sql_query(query, con)
    players_names = df['player_name'].to_list()
    return players_names

    
def load_games_summary(con): 
    return pd.read_sql_query('select * from games_summary', con)


import plotly 
import sqlite3
def generate_game_over_game_chart():

    query = '''

        SELECT 
            game_id
            , datetime(time, 'unixepoch', 'localtime') time
            , time as t
            , key 
            , count(key) over (partition by game_id order by time) key_count
            , time - min(time) OVER (PARTITION BY game_id) min_time
            , count(key) over (partition by game_id order by time) / ((time - min(time) OVER (PARTITION BY game_id)) / 60) / 5 wpm
            , rank() over (order by time) as rank
        FROM 
            keys_pressed
        where 
            correct_key = 1
        order by time

    '''


    df = pd.read_sql_query(query, con).query('wpm < 4000')
    fig = px.line(df, x='rank', y='wpm', title='WPM over time')
    fig = fig.update_layout(yaxis_range=[0, 500])
    return fig



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
        , avg(time_diff) - lag(avg(time_diff)) over(order by avg(time_diff)) diff
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

def plotthisgreatthing(con, letters=''):
    def character_ranking(con, max_key_count_to_use=None, min_key_count_to_use=None, condition1='', condition='', order='desc'): 
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
            {condition1}

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
            and c.type = 'lower_case_letter'
            {condition}
                
        group by key
        order by avg_time_diff {order}
        '''

        df  = pd.read_sql_query(query, con)
        df['time_diff'] = df['diff'].expanding().sum()
        return df 

    # character_ranking(con)
    con.execute('drop table if exists character_ranking_game_over_game')
    game_ids = query_table(con, 'keys_pressed').sort_values('time')['game_id'].unique().tolist()
    game_ids

    for index in range(len(game_ids)): 
        subset = ', '.join([str(game_ids[i]) for i in range(index)])
        df = character_ranking(con, condition1=f'and game_id in ({subset})')
        df['index'] = index
        df.to_sql('character_ranking_game_over_game', con, if_exists='append', index=False)


    df = pd.read_sql_query('select * from character_ranking_game_over_game', con).query('key in ("w", "x", "z")').round(4)
    return px.line(df, x='index', y='diff', color='key')#.update_layout(yaxis_range=[0, 0.2])


def avg_speed_per_letter(con, condition=''):
    query= f''' 

    with tbl as (
    select 
        key
        , game_id
        , time
        , lead(time) over(partition by game_id order by time desc) lead_time
        , time - lead(time) over(partition by game_id order by time desc) time_diff
        , row_number() over(partition by key order by time desc) letter_descending_rank 
        , datetime(time, 'unixepoch', 'localtime') date_time

    from keys_pressed
    where 1=1 
        and correct_key = 1
    order by time asc
    )

    select 
        key 
        , time 
        , lead_time
        , time_diff
        , letter_descending_rank
        , tbl.date_time
        , avg(time_diff) over(partition by key rows between 1000 preceding and current row) key_count

    from tbl
    left join games_summary gs using(game_id)
    where {condition}
    order by time asc
    '''

    df = pd.read_sql_query(query, con)
    return px.scatter(df, y='key_count', trendline='ols')