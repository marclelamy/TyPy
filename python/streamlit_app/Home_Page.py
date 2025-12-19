import streamlit as st 
from streamlit_autorefresh import st_autorefresh
import backend as b
import sqlite3





# File preference 
#######################################################
st.set_page_config(layout='wide', 
                   page_title='TyPy dashboard',
                   page_icon='📊')

# Auto refresh app 
# st_autorefresh(interval=5000, limit=100, key="fizzbuzzcounter")

# Session state 
if 'con' not in st.session_state:
    st.session_state.con = sqlite3.connect('data/main_database.sqlite')



# Sidebar   
with st.sidebar: 
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write('Tables')

    with st.spinner('Loading data...'):
        st.session_state.df_games_summary = b.load_table(st.session_state.con, 'games_summary')
        st.write('Games summary loaded ✅')
        st.session_state.df_keys_pressed = b.load_table(st.session_state.con, 'keys_pressed')
        st.write('Keys pressed loaded ✅')








# Main page
#######################################################
st.title("TyPy dashboard")







