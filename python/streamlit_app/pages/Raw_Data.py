import streamlit as st 




if 'df_games_summary' in st.session_state: 
    st.write('Games summary')
    st.dataframe(st.session_state.df_games_summary)

if 'df_keys_pressed' in st.session_state: 
    st.write('Keys pressed')
    st.dataframe(st.session_state.df_keys_pressed)