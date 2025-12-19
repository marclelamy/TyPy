import streamlit as st 
import pandas as pd
import numpy as np
# for random functions
from random import random
import numpy as np
import sqlite3
import pandas as pd
import time
import plotly.express as px
import os
from sklearn.linear_model import LinearRegression

current_dir = os.getcwd()

# # Load data from dbs
con = sqlite3.connect(f"/Users/marclamy/Desktop/code/pyFastType/main_database.db")


# # # @st.cache()
# # def load_data():
# #     # Get the score for each game with a word count > 20
# #     query_high_score = """
# #         with tb1 as (
# #         select
# #             game_id
# #             , datetime(max(time), 'unixepoch', 'localtime') Datetime
# #             , max(time) - min(time) game_duration
# #             , sum(case when correct_key = 1 then 1 else 0 end) keys_to_press
# #             , count(*) keys_pressed
# #             , round(CAST(sum(case when correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) * 100 accuracy
# #             , round(sum(case when correct_key = 1 then 1 else 0 end) / ((max(time) - min(time)) / 60) / 4.7, 2) wpm
# #             , row_number() over()

# #         from keys_pressed
# #         left join games_settings gs using(game_id)
# #         where 1=1
# #             and sentence_length >= 25
# #             and game_id > 100
# #         group by 1
# #         )

# #         select 
# #             *
# #             , row_number() over(order by Datetime asc) game_count
# #         from tb1
# #         order by Datetime asc

# #         """

# #     df_high_score = pd.read_sql_query(query_high_score, con)
# #     return df_high_score.iloc[:75]




# ############
# # Design
# ############
st.set_page_config(layout='wide', page_title='pyFastType dashboard')

# st.title('pyFastType Dashboard')

# df_high_score = load_data()



# # Regression
# reg = LinearRegression().fit(df_high_score[['game_count']], df_high_score[['wpm']])
# df_high_score['reg_line'] = reg.intercept_ + df_high_score['game_count'] * reg.coef_[0]


# st.subheader('WPM')
# st.line_chart(df_high_score['wpm'])
# st.write(f'Slope: {reg.coef_[0][0]}')
# st.line_chart(df_high_score[['wpm', 'reg_line']])





query = '''
    with tbl1 as (
    select
        key
        , lead(key) over(partition by game_id order by game_id, time) following_key
        , time
        , lead(time) over(partition by game_id order by game_id, time) following_time
        , game_id

    from keys_pressed
    where 1=1
        and correct_key = 1
        and game_id > 100
    )

    select 
        following_key
        , game_id
        , max(time)
        , avg(following_time - time) as time_diff
        , count(*) count

    from tbl1
    where 1=1
        and following_key is not null
    group by 2,1
    having 1=1
        -- and count > 100
    order by max(time) asc
    '''



def load_query () -> list:
    '''Opens a given text file name and execute the 
    query to return a pd.DataFrame
    
    Parameter
    ---------
    query_name str: name of the file name to run
    '''

    # Open file and get the query 
    # with open(f'{current_dir}/data/queries/{query_name}') as file: 
    #     query = file.read()

    # Query database
    df = pd.read_sql_query(query, con)

    return df
 

df = load_query()
letter = st.select_slider(
    'Select a color of the rainbow',
    options='abcdefghijklmnopqrstuvwxyz')

st.line_chart(df.query('following_key == @letter')['time_diff'], df.query('following_key == @letter').index)