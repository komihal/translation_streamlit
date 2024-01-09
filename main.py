import streamlit as st
import pandas as pd
import sqlite3
import nltk
from nltk.corpus import brown
from collections import Counter

# Загрузка корпуса Brown
nltk.download('brown')

# Функция для генерации датасета с частотами слов
def generate_dataset(num_rows):
    words = brown.words()
    words = [word.lower() for word in words if word.isalpha()]
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(num_rows)

    df = pd.DataFrame(most_common_words, columns=['word', 'frequency'])
    df['already_known'] = False  # Добавление колонки already_known
    return df

# Подключение к базе данных
conn = sqlite3.connect('DB_streamlit_translate.db')

# Создание таблицы с дополнительной колонкой Frequency
with conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS english_dictionary (
            word TEXT, 
            already_known BOOLEAN,
            frequency INTEGER
        );
    ''')

# Загрузка данных из базы данных
def load_data(conn):
    df = pd.read_sql_query('SELECT * FROM english_dictionary', conn)
    if not df.empty:
        df['already_known'] = df['already_known'].astype(bool)
    return df

# Настройка Streamlit
st.set_page_config(layout="centered", page_title="Data Editor", page_icon="🧮")
st.title("Личный список слов")

df_personal_dictionary = load_data(conn)
if df_personal_dictionary.empty:
    if st.button('Generate New Word List'):
        df_personal_dictionary = generate_dataset(1000)
        df_personal_dictionary.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.write("Новый список сгенерирован!")

# Функция для сохранения данных в базу данных
def save_to_database(df, conn):
    with conn:
        df.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.success("Data saved to database successfully!")

with st.form("data_editor_form"):
    edited = st.data_editor(df_personal_dictionary, use_container_width=True)
    submit_button = st.form_submit_button("Внести правки")

if submit_button:
    save_to_database(edited, conn)
    st.expander("Edited dataset", expanded=True).dataframe(edited, use_container_width=True)
    st.experimental_rerun()

conn.close()

