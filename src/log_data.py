# from turtle import pu
# import numpy as np
# import pygame
import sqlite3
import pandas as pd
# from tabulate import tabulate
# import time
# # from PyDictionary import PyDictionary
# import os
# from pyparsing import conditionAsParseAction
# from termcolor import colored

# from src.score import Score
# from src.log_data import *

pd.set_option('display.float_format', lambda x: '%.2f' % x)
# pygame.init()
con = sqlite3.connect("main_database.db")
# current_dir = os.getcwd()







def log_key_pressed(key_pressed):
    column_names = ['key', 'correct_key', 'time', 'game_id']
    df_keys = pd.DataFrame(key_pressed, columns=column_names)
    df_keys.to_sql('keys_pressed', con, if_exists='append', index=False)


def log_game_settings(game_settings):
    column_names = ['game_id', 'game_settings']
    # game_settings_lst = [game_settings['game_id'], str({key:value if key != 'game_id'game_settings})]
    game_id = game_settings['game_id']
    del game_settings['game_id']
    df_game_settings = pd.DataFrame([[game_id, str(game_settings)]], columns=column_names)
    df_game_settings.to_sql('games_settings', con, if_exists='append', index=False)


def clean_games_settings():
    df = pd.read_sql_query('select distinct * from games_settings', con)
    df['game_settings'] = df['game_settings'].apply(lambda x: eval(x))
    df_games_settings = pd.concat([df[['game_id']], df['game_settings'].apply(lambda x: pd.Series(x))], axis=1)
    df_games_settings.drop_duplicates().to_sql('clean_games_settings', con, if_exists='replace', index=False)


def log_summary_per_game(): 
    query = f"""
        select
            distinct
            kp.game_id
            , max(kp.time) maxdatetime_unix
            , min(kp.time) mindatetime_unix
            , max(kp.time) - min(kp.time) game_duration
            , sum(case when kp.correct_key = 1 then 1 else 0 end) keys_to_press
            , count(*) keys_pressed
            , round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) accuracy
            , sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5 wpm
            , length(cgs.sentence) sentence_length
            , length(cgs.sentence) * (sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5) * round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) score
            , cgs.sentence
            , cgs.word_count
            , cgs.max_word_length	
            , cgs.capitalized_words_count	
            , cgs.capitalized_letters_count_perc	
            , cgs.punctuation_word_count_perc	
            , cgs.force_shift	
            , cgs.hard_mode	
            , cgs.train_letters	
            , cgs.comment	
            , LOWER(cgs.player_name)

        from keys_pressed kp 
        left join clean_games_settings cgs using(game_id)
        where 1=1
        group by 1
        order by maxdatetime_unix asc
        """

    df_high_score = pd.read_sql_query(query, con)
    df_high_score.to_sql('summary_per_game', con, if_exists='replace', index=False)




def push_to_gbq():
    df_keys_pressed = pd.read_sql_query('select * from keys_pressed', con)
    df_keys_pressed.to_gbq('pyfasttype.keys_pressed', if_exists='replace', progress_bar=None)
    df_clean_games_settings = pd.read_sql_query('select * from clean_games_settings', con)
    df_clean_games_settings['capitalized_letters_count_perc'] = df_clean_games_settings['capitalized_letters_count_perc'].astype(str)
    df_clean_games_settings.to_gbq('pyfasttype.clean_games_settings', if_exists='replace', progress_bar=None)
    # df_summary_per_game = pd.read_sql_query('select * from summary_per_game', con)
    # df_summary_per_game.to_gbq('pyfasttype.summary_per_game', if_exists='replace', progress_bar=None)
    print('Data pushed to GBQ')