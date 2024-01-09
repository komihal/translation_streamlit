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

# Функция для генерации датасета
def generate_dataset(num_rows):
    dataset = []

    for _ in range(num_rows):
        word = random.choice(list(stop_words))
        boolean_value = False  # Изначально все значения False
        dataset.append((word, boolean_value))

    return pd.DataFrame(dataset, columns=['word', 'already_known'])

# Подключение к базе данных
conn = sqlite3.connect('DB_streamlit_translate.db', check_same_thread=False)

# Создание таблицы, если она не существует
conn.execute('CREATE TABLE IF NOT EXISTS english_dictionary (word TEXT, already_known BOOLEAN);')

# Проверка наличия данных в базе данных
df_personal_dictionary = pd.read_sql_query('SELECT * FROM english_dictionary', conn)
if df_personal_dictionary.empty:
    # Если база данных пуста, генерируем новые данные и сохраняем их
    df_personal_dictionary = generate_dataset(1000)
    df_personal_dictionary.to_sql('english_dictionary', conn, if_exists='replace', index=False)
else:
    # Преобразование типа данных для булевой колонки
    df_personal_dictionary['already_known'] = df_personal_dictionary['already_known'].astype('bool')

# Отображение данных с помощью AgGrid
st.write("Data loaded from database:")
grid_response = AgGrid(df_personal_dictionary, editable=True, fit_columns_on_grid_load=True)

# Получение отредактированных данных
edited_df = grid_response['data']

# Функция для сохранения изменений в базу данных
def save_changes():
    with conn:
        edited_df.to_sql('english_dictionary', conn, if_exists='replace', index=False)
        st.success("Changes saved to database successfully!")

# Кнопка для сохранения изменений
if st.button("Save Changes"):
    save_changes()

conn.close()
