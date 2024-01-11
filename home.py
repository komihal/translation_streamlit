import streamlit as st
import requests
from lxml import html
import sqlite3
import pandas as pd
import string
import spacy
import translators as ts
import re
from tqdm.auto import tqdm
import spacy
import streamlit as st


def is_number_repl_isdigit(s):
    """ Returns True if string is a number. """
    return s.replace('.','',1).isdigit()

def translate(text):
    for i in ['translateCom','bing','google','baidu']:
        try:
            w = ts.translate_text(query_text = text, translator = i, from_language= 'en', to_language = 'ru').lower()
            return w
        except:
            pass
    return "Error"

def get_text_from_subtitles(parsed_subtitles):
  # full_text = ' '.join([text['text'] for text in parsed_subtitles])
  full_text = parsed_subtitles
  regex = re.compile("[^a-zA-Z' а-яА-ЯЁё.,!?-]")
  sentence = regex.sub(' ', full_text)  # Remove unwanted characters
  sentence = re.sub(r'\s+', ' ', sentence).strip()  # Normalize spaces
  sentence = re.sub(r"in\' ", 'ing ', sentence)  # Replace "in' " with "ing "# Combine standard punctuation with apostrophes
  all_punctuations = string.punctuation
  for punct in all_punctuations:
      full_text = full_text.replace(punct, ' ')
  full_text = re.sub(r'\s+', ' ', full_text)
  return full_text

def get_lemmas_and_originals(full_text):
  
  doc = nlp(full_text)
  stop_list = ('not', 'to')
  lemmas = [token.lemma_ for token in doc if token.lemma_ not in stop_list and not " " in token.lemma_]
  orig_words = [word for word in full_text.split() if word.lower() not in stop_list]
  # i = 0
  # for lem, orig in zip(lemmas, orig_words):
  #   i += 1
  #   print(i, lem, orig)
  return lemmas, orig_words

def needed_words(i, lemma):
    frequency_lemma_list.append((frequency_lemma, lemma))
    # for subtitle in parsed_subtitles:
    #   examp = subtitle['text'].replace('\n', ' ')
    #   if orig_words[i] in examp:
    #     break
    pattern = "[" + string.punctuation + "]"
    split_text = re.split(pattern, parsed_subtitles)
    split_text = [s.strip() for s in split_text if s]
    for examp in split_text:
      examp = examp.replace('\n', ' ')
      if orig_words[i] in examp:
        break
    lemma_translation = translate(lemma)
    examp_translation = translate(examp)
    dict_words[lemma] = (orig_words[i], lemma_translation, examp, examp_translation, frequency_lemma)
    return dict_words, frequency_lemma_list

def load_data(conn):
    df = pd.read_sql_query('SELECT * FROM english_dictionary', conn)
    df['already_known'] = df['already_known'].astype(bool)
    return df



with st.form("load_url", border=False):
    url = st.text_input(label="URL подкаста или фильма", value="https://www.thisamericanlife.org/205/transcript")
    submit_button = st.form_submit_button("Загрузить субтитры")

parsed_subtitles = 0 

if submit_button:
    #@title Загрузка подкаста

    response = requests.get(url)
    tree = html.fromstring(response.content)

    # XPath to target the specific part of the page
    xpath = '//*[@id="block-system-main"]/div/article/div[2]'
    text = tree.xpath(xpath)[0].text_content()  # Adjust index [0] as necessary
    parsed_subtitles = text
    st.session_state["parsed_subtitles"] = parsed_subtitles



###### Обработка всех Лемм


if st.session_state['parsed_subtitles']:
  parsed_subtitles = st.session_state['parsed_subtitles']

if parsed_subtitles:
    with st.expander (label="загруженные субтитры"): 
        st.write(parsed_subtitles)
else:
   st.write("пока нет загруженных субтитров")

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])


conn = sqlite3.connect('DB_streamlit_translate.db')
nlp = spacy.load("en_core_web_sm")


lemmas_df = load_data(conn)
lemmas_df = lemmas_df.set_index('word')
vocabulary_dict = lemmas_df['frequency_rank'].to_dict()
studied_lemmas = set(lemmas_df[lemmas_df['already_known']].index)


MIN_FREQUENCY = 4000
MAX_FREQUENCY = 10000


seen_lemmas_cur_movie = set()
non_dictionary_words = set()
# over_maximum_words = set()
frequency_lemma_list = []
dict_words = {}

full_text = get_text_from_subtitles(parsed_subtitles)
lemmas, orig_words = get_lemmas_and_originals(full_text)

if submit_button:
    st.write("DF сравнения")

progress_bar = st.progress(0)
total = len(lemmas)
for i, lemma in enumerate(tqdm(lemmas)):
    progress_bar.progress((i + 1) / total)

    if (lemma in seen_lemmas_cur_movie) or (lemma in studied_lemmas) or (len(lemma) < 4):
      continue
    # st.write("1")
    seen_lemmas_cur_movie.add(lemma)

    if lemma not in vocabulary_dict:
      non_dictionary_words.add(lemma[1])
      continue

    frequency_lemma = vocabulary_dict[lemma]
    # if frequency_lemma>MAX_FREQUENCY:
    #   over_maximum_words.add(lemma)
    #   continue

    if frequency_lemma > MIN_FREQUENCY:
      # print(lemma)
      studied_lemmas.add(lemma)
      dict_words, frequency_lemma_list = needed_words(i, lemma)
      # break

st.write(dict_words)
# for k,v in vocabulary_dict.items():
#   st.write(k, v)   
#   break
