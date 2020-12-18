# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 14:44:24 2020

@author: Faroud
"""
# %% Imports

import os, inspect
import pickle


from tensorflow.keras.models import load_model
# %%

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
#print(src_dir)
data_dir = os.path.abspath(os.path.join(src_dir, 'data/'))

ENGLISH_VOCAB_FILE_PATH = os.path.join(data_dir, 'english_vocab')
FRENCH_VOCAB_FILE_PATH = os.path.join(data_dir, 'french_vocab')

ENGLISH_MODEL_PATH = os.path.join(data_dir, 'englishModel.h5')
FRENCH_MODEL_PATH = os.path.join(data_dir, 'frenchModel.h5')


# %% Utility function

# load the vocabulary from file
def __load_vocabulary(vocabulary_file_path):
    vocab = None
    try:
        with open (vocabulary_file_path, 'rb') as fp:
            vocab = pickle.load(fp)
    except FileNotFoundError as er:
        print(f"Vocabulary file not Found: {er}")
    finally:
        return vocab
# end load_vocab

def load_english_vocabulary():
    return __load_vocabulary(ENGLISH_VOCAB_FILE_PATH)

def load_french_vocabulary():
    return __load_vocabulary(FRENCH_VOCAB_FILE_PATH)



# %% models loader

# function to load the model to use
def load_english_model():
    return load_model(ENGLISH_MODEL_PATH)


def load_french_model():
    return load_model(FRENCH_MODEL_PATH)

# %%