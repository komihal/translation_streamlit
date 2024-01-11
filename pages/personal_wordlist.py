import streamlit as st
import pandas as pd
import sqlite3
import nltk
# from nltk.corpus import brown
from collections import Counter


# Функция для генерации датасета с частотами слов
def generate_dataset():
    df = pd.read_csv("lemmas.csv")
    df.columns = ['word', 'frequency_rank', 'already_known']
    return df


# Подключение к базе данных
conn = sqlite3.connect('DB_streamlit_translate.db')

# Создание таблицы с дополнительной колонкой Frequency
with conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS english_dictionary (
            word TEXT, 
            already_known BOOL,
            frequency_rank INTEGER
        );
    ''')

# Загрузка данных из базы данных
def load_data(conn):
    df = pd.read_sql_query('SELECT * FROM english_dictionary', conn)
    if not df.empty:
        df['already_known'] = df['already_known'].astype(bool)
    return df

# Настройка Streamlit
st.set_page_config(layout="wide", page_title="Персональный лист слов", page_icon="🧮")
st.write("Личный список слов", )

df_personal_dictionary = load_data(conn)
if df_personal_dictionary.empty:
    if st.button('Activate New Word List'):
        df_personal_dictionary = generate_dataset()
        df_personal_dictionary.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.write("Новый список сгенерирован!")

# Функция для сохранения данных в базу данных
def save_to_database(df, conn):
    with conn:
        df.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.success("Data saved to database successfully!")

with st.form("data_editor_form", border=False):
    edited = st.data_editor(df_personal_dictionary, use_container_width=True, height=500)
    submit_button = st.form_submit_button("Внести правки")

if submit_button:
    save_to_database(edited, conn)
    st.expander("Edited dataset", expanded=True).dataframe(edited, use_container_width=True)
    st.rerun()

conn.close()

