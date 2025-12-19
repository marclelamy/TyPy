# http://localhost:8501/Plotting_Demo
# https://docs.streamlit.io/library/cheatsheet


import streamlit as st
import time
import pandas as pd
import numpy as np

st.set_page_config(layout='wide', 
                   page_title='pyFastType dashboard',
                   page_icon='📊')
value = st.slider('time_wait', min_value=0.0001, max_value=0.001, value=0.0001, step=0.000001),


progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
chart = st.line_chart(last_rows)



for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)        
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0)

progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")

tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
tab1.write("this is tab 1")
tab2.write("this is tab 2")



st.text('Fixed width text')
st.markdown('_Markdown_') # see *
st.latex(r''' e^{i\pi} + 1 = 0 ''')
st.write('Most objects') # df, err, func, keras!
st.write(['st', 'is <', 3]) # see *
st.title('My title')
st.header('My header')
st.subheader('My sub')
st.code('for i in range(8): foo()')

my_dataframe = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
st.dataframe(my_dataframe)
st.table(my_dataframe.iloc[0:10])
st.json({'foo':'bar','fu':'ba'})
st.metric('My metric', 42, 2)

# Just add it after st.sidebar:
a = st.sidebar.radio('Select one:', [1, 2])
# Or use "with" notation:
with st.sidebar:
  q = st.radio('Select one or two:', [1, 2])


st.write(a)







# Two equal columns:
col1, col2 = st.columns(2)
col1.write("This is column 1")
col2.write("This is column 2")
# You can also use "with" notation:
with col1:
    st.write('duuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuu')

with col2: 
    st.write('duuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuu')

# Three different columns:
col1, col2, col3 = st.columns([3, 1, 1])
col1.write("This is column 1")
col2.write("This is column 2")
col3.write("This is column 3")

# You can also use "with" notation:
with col1:
    st.write('duuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuu')

with col2: 
    st.write('duuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuu')

with col3:
    st.write('duuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuuduuuu')
