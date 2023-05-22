import streamlit as st 
# from streamlit_autorefresh import st_autorefresh
import pandas as pd
# import sqlite3
import backend as mb
import datetime

import plotly.io as pio

pio.templates.default = "plotly_dark"


# File preference 
#######################################################
st.set_page_config(layout='wide', 
                   page_title='TyPy dashboard',
                   page_icon='📊')




# Load data 
#######################################################
df_games_settings = mb.load_game_settings()
total_time_played = mb.time_played()
df_games_summary = mb.load_games_summary()




# Start design
#######################################################
# Title 
st.title('TyPy dashboard', )





# Top Metrics
total_games = df_games_summary['game_id'].unique().shape[0]
avg_accuracy = df_games_summary['accuracy'].mean()
avg_accuracy_past_100_games = df_games_summary['accuracy'].tail(100).mean()
avg_wpm = df_games_summary['wpm'].mean()
avg_wpm_past_100_games = df_games_summary['wpm'].tail(100).mean()

_, metrics_col1, metrics_col2, metrics_col3, _ = st.columns(5)
with metrics_col1:
    st.metric('Games Played', f'{total_games:,}')

with metrics_col2:
    st.metric('Time Played', (str(datetime.timedelta(seconds=total_time_played)).replace(' days, ', 'd ').replace(' day, ', 'd ').replace(':', 'h ').replace(':', 'm ') + 's').upper()) # brilliant engineering here i must admit

with metrics_col3:
    st.metric('Avg Accuracy', f'{avg_accuracy:.1%}')



st.plotly_chart(mb.generate_game_over_game_chart())


# Overtime wpm and accuracy 
for x in range(2): 
    st.write('')

sentence_length_min = st.slider(
    label = "Sentence length min:",
    min_value = int(df_games_summary['word_count'].min()), 
    max_value = int(df_games_summary['word_count'].max()), 
    value = 70, 
    step = 1)
# games_validating_slider_count = df....



for x in range(100): 
    st.write('')

# Display full table of summary
st.dataframe(df_games_summary)


















































































































































































































































































































































































































































































#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
# Below is old code that I keep for reference
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
##############################################################################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
##############################################################################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
##############################################################################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################








# import streamlit as st 
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# # import sqlite3
# from main_backend import *
# import datetime

# import plotly.io as pio

# pio.templates.default = "plotly_dark"


# # File preference 
# #######################################################
# st.set_page_config(layout='wide', 
#                    page_title='pyFastType dashboard',
#                    page_icon='📊')




# Load data 
#######################################################
# df_games_settings = load_game_settings()
# total_time_played = time_played()




# Main design
#######################################################
# st.columns([1, 1, 1])[1].title('pyFastType dashboard')


# top_ = st.columns([2, 1, 1, 1, 2])
# with five_cols[1]:
#     st.write('Games Played', df_games_settings.shape[0])
# with five_cols[2]:
#     st.write('Time Played', str(datetime.timedelta(seconds=total_time_played)))    
























################################################################################
# tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
# tab1.write("this is tab 1")
# tab2.write("this is tab 2")

# with tab2:
#     # Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
#     # after it's been refreshed 100 times.
#     # count = st_autorefresh(interval=10, limit=100000, key="fizzbuzzcounter")

#     # # The function returns a counter for number of refreshes. This allows the
#     # # ability to make special requests at different intervals based on the count
#     # if count == 0:
#     #     st.write("Count is zero")

#     # else:
#     #     st.write(f"Count: {count}")

#     st_autorefresh(interval=5000)





#### 
# import plotly.express as px
# import streamlit as st

# df = px.data.gapminder()

# fig = px.scatter(
#     df.query("year==2007"),
#     x="gdpPercap",
#     y="lifeExp",
#     size="pop",
#     color="continent",
#     hover_name="country",
#     log_x=True,
#     size_max=60,
# )

# tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
# with tab1:
#     # Use the Streamlit theme.
#     # This is the default. So you can also omit the theme argument.
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
# with tab2:
#     # Use the native Plotly theme.
#     st.plotly_chart(fig, theme=None, use_container_width=True)