# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 15:57:06 2020

@author: Faroud
"""
# %% Imports
import nltk
#nltk.download()
from stop_words import get_stop_words
import string
from spellchecker import SpellChecker
from nltk.stem.snowball import FrenchStemmer, EnglishStemmer
from nltk.stem import WordNetLemmatizer


import pandas as pd
import itertools

# %%
printable = string.printable
additional_french_stop_words = ['lire', 'opinion', 'plus', 'voilà', 'après', 'i', 'iii', 'iv', 'vi', 'xv']
additional_english_stop_words = []


# %% Functions

def basic_preprocessing(data: pd.DataFrame, lang: str):
    """According to the language passed in, we apply some corresponding preprocessing.
    Here we assume that we know the structure of the data(the column name ...)
    -----------------------------
    document          | category |
    -----------------------------|
    "He scored a goal"| SPORT    |
    ------------------|----------|
    """
    
    spell = SpellChecker(language=lang)
    def spellCorrector(text):
        return " ".join(spell.correction(word) for word in text.split())
    # end spellCorrector
    
    def build_complete_stop_words(lang: str):
        complete_stop_words =  get_stop_words(lang)
        if (lang == 'fr'):
            complete_stop_words += additional_french_stop_words
        else:
            complete_stop_words += additional_english_stop_words
        return complete_stop_words
    # end build_complete_stop_words  
    
    pro_data = data.copy(deep=True)
    #strip out white spaces and lower all character then remove punctuations an numerical values
    pro_data['document'] = pro_data['document'].apply(lambda text: " ".join(word.strip().lower() for word in text.split())) \
        .str.replace('[^\w\s]|\d', ' ') \
        .apply(lambda text: " ".join(word for word in text.split() if len(word) > 1))
    # after removing the punctuation, we get some trash letter we removed vith the line above. 
    
    # remove stop words and correct spelling and then tokenize to make the following 
    # prprocess step easy
    stop_words = build_complete_stop_words(lang)
    pro_data['document'] = pro_data['document'] \
        .apply(lambda text: " ".join(word for word in text.split() if word not in stop_words)) \
        .apply(lambda text: nltk.word_tokenize(text))
    
    # Stemming (extraction of the root word) and lemmetization
    #st = nltk.stem.PorterStemmer()
    st = FrenchStemmer() if lang == "fr" else EnglishStemmer()
    lemmatizer = WordNetLemmatizer()
    pro_data['document'] = pro_data['document'] \
        .apply(lambda token_list: list(map(lambda word: st.stem(word), token_list))) \
        .apply(lambda token_list: list(map(lambda word: lemmatizer.lemmatize(word, pos="v"), token_list)))
    return pro_data
# end basic preprocessing


def frequent_and_rare_words(data):
    frequency_dist = nltk.FreqDist(
        list(itertools.chain(*data['document'].values))
    )
    # sort the word in the vocabulary
    sorted_frequency_dist = sorted(frequency_dist, key=frequency_dist.__getitem__, reverse=True)
    
    most_frequent_words = sorted_frequency_dist[:10]
    # word with frequency less than 5
    less_frequent_words = list(filter(lambda word: frequency_dist[word] <= 5, sorted_frequency_dist))
    
    final_vocabulary = list(filter(
        lambda word: word not in most_frequent_words + less_frequent_words, sorted_frequency_dist
    ))
    return final_vocabulary, most_frequent_words, less_frequent_words
# end frequent_and_rare_words


def preprocessing_further(data, further=True):
    """
    """
    # remoove frequent and rare words from the text
    pro_data = data.copy(deep=True)
    vocabulary, frequent_words, rare_words = frequent_and_rare_words(pro_data)
    if further:
        words_to_delete = set(frequent_words + rare_words)
        pro_data['document'] = pro_data['document'].apply(
            lambda token_list: list(filter(lambda token: token not in words_to_delete, token_list))
        )
    else:
        pass
    pro_data['document'] =  pro_data['document'].apply(lambda token_list: " ".join(token_list))
    return vocabulary, pro_data
# end preprocessing_further


def text_preprocessing(data, lang: str, deep: bool = False):
    """
    """
    if lang not in['fr', 'en']: 
        return None
    else:
        return preprocessing_further(
            basic_preprocessing(data, lang), further=deep
        )
# end text_preprocessing 