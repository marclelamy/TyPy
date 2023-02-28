# import streamlit as st 
import pandas as pd
import sqlite3
import streamlit as st



con = sqlite3.connect('data/main_database.db')



def time_played() -> int:
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


st.cache()
def load_game_settings(): 
    query = '''
            select 
                *

            from clean_games_settings
            '''

    df = pd.read_sql_query(query, con)
    return df


def list_players() -> int:
    query = '''
            select 
                distinct 
                player_name
            from clean_games_settings
            '''

    df = pd.read_sql_query(query, con)
    players_names = df['player_name'].to_list()
    return players_names

    
def load_games_summary(): 
    return pd.read_sql_query('select * from games_summary', con)