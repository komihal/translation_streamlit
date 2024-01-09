import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import sqlite3

# df = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv')
# AgGrid(df)

conn = sqlite3.connect('DB_streamlit_translate.db')

# Insert some data with conn.session.
with conn:
    conn.execute('CREATE TABLE IF NOT EXISTS english_dictionary (word TEXT, already_known BOOLEAN);')
    conn.execute('DELETE FROM english_dictionary;')
    started_dictionary = {'jerry': 'FALSE', 'barbara': 'FALSE', 'alex': 'TRUE'}
    for word, already_known in started_dictionary.items():
        conn.execute('INSERT INTO english_dictionary (word, already_known) VALUES (?, ?);', (word, already_known))

# Query and display the data
df_personal_dictionary = pd.read_sql_query('SELECT * FROM english_dictionary', conn)

AgGrid(df_personal_dictionary)
# Close the connection

df_personal_dictionary.already_known = df_personal_dictionary.already_known.astype('bool') 

st.write(df_personal_dictionary.dtypes)
edited_df = st.data_editor(df_personal_dictionary, num_rows="dynamic") 

conn.close()
