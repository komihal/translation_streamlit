import random
import pandas as pd
import streamlit as st
import nltk
from nltk.corpus import stopwords
import sqlite3


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

    return pd.DataFrame(dataset, columns=['Word', 'Boolean'])

# Генерация датасета
dataset = generate_dataset(1000)


conn = sqlite3.connect('DB_streamlit_translate.db')


st.write("Length of dataset: ", len(dataset))
with st.form("data_editor_form"):
    st.caption("Edit the dataframe below")
    edited = st.data_editor(dataset, use_container_width=True)
    submit_button = st.form_submit_button("Submit")

# Функция для сохранения данных в базу данных
def save_to_database(df, conn):
    with conn:
        df.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.success("Data saved to database successfully!")



if submit_button:
    save_to_database(edited, conn)
    st.expander("Edited dataset", expanded=True).dataframe(edited, use_container_width=True)