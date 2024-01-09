import streamlit as st
import pandas as pd
import sqlite3
import random
import nltk
from nltk.corpus import stopwords

# Загрузка стоп-слов
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Установка начальных значений для генераторов случайных чисел
random.seed(0)

# Настройка Streamlit
st.set_page_config(layout="centered", page_title="Data Editor", page_icon="🧮")
st.title("🏗 Big Data Editor")
st.caption("This is a demo of the `st.data_editor`.")

# Функция для генерации датасета
def generate_dataset(num_rows):
    dataset = []

    for _ in range(num_rows):
        word = random.choice(list(stop_words))
        boolean_value = False  # Изначально все значения False
        dataset.append((word, boolean_value))

    df = pd.DataFrame(dataset, columns=['Word', 'Boolean'])
    df['Boolean'] = df['Boolean'].astype(bool)  # Установка типа данных колонки как bool
    return df

# Подключение к базе данных
conn = sqlite3.connect('DB_streamlit_translate.db')

# Загрузка данных из базы данных
def load_data(conn):
    df = pd.read_sql_query('SELECT * FROM english_dictionary', conn)
    df['already_known'] = df['already_known'].astype(bool)  # Установка типа данных колонки как bool
    return df

# Отображение данных из базы данных
df_personal_dictionary = load_data(conn)
st.write("Data loaded from database:")
st.dataframe(df_personal_dictionary)

# Кнопка для генерации списка слов
if st.button('Generate Word List'):
    dataset = generate_dataset(1000)
    st.write("Generated dataset with 1000 words")
    st.dataframe(dataset)

# Функция для сохранения данных в базу данных
def save_to_database(df, conn):
    with conn:
        df.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.success("Data saved to database successfully!")

with st.form("data_editor_form"):
    edited = st.data_editor(df_personal_dictionary, use_container_width=True)
    submit_button = st.form_submit_button("Submit")

if submit_button:
    save_to_database(edited, conn)
    st.expander("Edited dataset", expanded=True).dataframe(edited, use_container_width=True)

conn.close()
