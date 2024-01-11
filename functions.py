import pandas as pd
import string
import spacy
import translators as ts
import random
import re
import numpy as np
import pickle
import os
from tqdm.auto import tqdm
import requests
import zipfile
import io
from datetime import datetime


#@title Функции ???  orig_words[i] in examp: проверяет включение слова в пример, а не полное совпадение
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
    split_text = re.split(pattern, text)
    split_text = [s.strip() for s in split_text if s]
    for examp in split_text:
      examp = examp.replace('\n', ' ')
      if orig_words[i] in examp:
        break
    lemma_translation = translate(lemma)
    examp_translation = translate(examp)
    dict_words[lemma] = (orig_words[i], lemma_translation, examp, examp_translation, frequency_lemma)
    return dict_words, frequency_lemma_list