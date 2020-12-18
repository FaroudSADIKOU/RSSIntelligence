# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 00:06:39 2020

@author: Faroud
"""
import classif_utils as cutils
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import preprocessing

import numpy as np
import pandas as pd
import preprocessing as prepro
# %%

labels = {
    0: "ART_CULTURE", 
    1: "ECONOMIE", 
    2: "POLITIQUE", 
    3: "SANTE_MEDECINE", 
    4: "SCIENCE", 
    5: "SPORT"
}

# %%
class Classifier:
    def __init__(self):
        # load all vocabulary
        self.french_vocabulary = cutils.load_french_vocabulary()
        self.english_vocabulary = cutils.load_english_vocabulary()
        
        # load both the french and english model
        self.french_model = cutils.load_french_model()
        self.english_model = cutils.load_english_model()
        #
        self.french_vectorizer = TfidfVectorizer(
            analyzer='word', token_pattern=r'\w{1,}', vocabulary = self.french_vocabulary
        )
        self.english_vectorizer = TfidfVectorizer(
            analyzer='word', token_pattern=r'\w{1,}', vocabulary = self.english_vocabulary
        )
        
        
    def predict(self, lang: str, text: str):
        lang = lang.lower() # lower is important here
        _, data = prepro.text_preprocessing(
            pd.DataFrame([text], columns=(['document'])), 
            lang, 
            False
        )
        
        vectorizer = self.__get_vectorizer(lang)
        if(vectorizer != None ):
            X_vectorized = vectorizer.fit_transform(data['document']).toarray()
             
            model = self.__get_model(lang)
            # perform predictions
            if model != None:
                predictions_probs = model.predict(X_vectorized)
                # get predicted class
                predicted = list(
                    map(
                        lambda prob: labels[prob],
                        np.argmax(predictions_probs, axis=1).tolist()
                        
                    )
                )
                return predicted[0]
            else:
                return None
        else:
            return None
    # end predict
    
         
    def __get_model(self, lang: str):
        if (lang == 'en'):
            return self.english_model
        if (lang == 'fr'):
            return self.french_model
        else:
            return None
    
    def __get_vectorizer(self, lang: str):
        if (lang == 'en'):
            return self.english_vectorizer
        if (lang == 'fr'):
            return self.french_vectorizer
        else:
            return None