# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 19:21:22 2020

@author: Faroud

Searcher module.
Get user request from a PySimpleGUI interface, 
Process the text,
Call the Word2Vec model to get some similar word to enrich user request,
Request data from the database with the new enriched query.
Send top ten request back to user via the iterface.
"""
# %% imports
import os, sys, inspect
import PySimpleGUI as sg

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
helper_dir = os.path.join(src_dir, "../helper")
sys.path.append(helper_dir)

from ElasticConnector import ElasticConnector
from gensim.models import KeyedVectors

import itertools
from langdetect import detect

data_dir = os.path.abspath(os.path.join(src_dir, 'data/'))

ENGLISH_WORDVECTORS_FILE_PATH = os.path.join(data_dir, 'english_word2vec.wordvectors')
FRENCH_WORDVECTORS_FILE_PATH = os.path.join(data_dir, 'french_word2vec.wordvectors')

# %%
class Searcher(): #ItemSearcher
    def __init__(self):
        self.client = ElasticConnector().connect()
        self.index_name = "users_feed_items"
        self.english_wordvectors = self.__init_wordvectors("en")
        self.french_wordvectors = self.__init_wordvectors("fr")
        
        
    def __init_wordvectors(self, lang: str):
        """ Load back with memory-mapping = read-only, shared across processes.
        """
        wv = None
        if (lang == "en"):
            wv = KeyedVectors.load(ENGLISH_WORDVECTORS_FILE_PATH, mmap='r')
        if (lang == "fr"):
            wv = KeyedVectors.load(FRENCH_WORDVECTORS_FILE_PATH, mmap='r')
        return wv
    # end __load_wordvectors
    
    def get_search_body_blue_print(self, lang: str):
        """ Define the blue print of a request 
        """
        return {
            "query":{
                "bool": {
                    "must":[
                        {"match": {"language": lang}},
                        {"bool": {
                             "should": [
                                 # this will be filled dynamically
                            ]
                        }  
                        }
                    ]   
                    }
                }
            }
    # end set_search_pattern
    
    def launch(self):
        """ Show the interface to help user request infos from 
        the elasticsearch database
        """
        # All the stuff inside the window.
        sg.theme('Dark Blue 3')
        layout = [  
            [sg.Text('SEARCHER', size=(100, 1), justification='center')],
            [sg.InputText(), sg.Button('search')] ,
            [sg.Multiline(size=(80, 20), key='-OUTPUT-')]
        ]
        
        # Create the Window
        window = sg.Window('SEARCHER', layout, size=(500, 300), element_justification='c')
        
        #print("Before WHILE")
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            # search is pressed
            result = self.search(values[0])
            window['-OUTPUT-'].update(result)
        window.close()
        
    
    def search(self, plain_text: str):
        """
        Search for documents with contents close to the users request
        """
        if(plain_text.strip() != ""):
            # detect the language
            lang = self.__detect_query_lang(plain_text)
            # get set of similar words (add the original words)
            similars = self.__get_similar_words(self.__plain_text_treatment(plain_text), lang)
            #print(similars)
            # build the request
            query_body = self.get_search_body_blue_print(lang)
            # TODO
            for token in similars:
                query_body['query']['bool']['must'][1]['bool']['should'].append(
                    {
                        "multi_match" : {
                            "query":    token, 
                            "fields": [ "title", "description", "content" ],
                        }
                    },
                    
                )       
                
            # launch the request and get the first ten of the results
            result_to_send = ""
            # check server availability
            if(self.client.ping()):
                # make sure the inde_name exists:
                if(self.client.indices.exists(self.index_name)):
                    res = self.client.search(
                        index=self.index_name,
                        body=query_body
                    )
                    #
                    #result_to_send = res['hits']['total']
                    result_to_send = self.__get_at_most_first_ten_formated_result(res)
                else:
                    result_to_send = "INDEX DOESN'T EXIST YET. WAIT FOR END OF CRAWLING..."
            else:
                result_to_send = "COULD NOT REACH SERVER"
            return result_to_send
    # end search
    
    
    def __get_similar_words(self, tokens, lang):
        """
        Using the wordvectors from the word2vec model get 
        similar words of the vocabulary 
        """
        # get the worvectors based on the language
        wordvectors = self.__get_wordvectors_by_lang(lang)
        #print(wordvectors)
        
        def inner_most_similar(token):
            if wordvectors != None:
                similars_list=None
                try:
                    similar_with_probs = wordvectors.most_similar(token)
                    similars_list = list(map(lambda a_tuple: a_tuple[0], similar_with_probs))
                except KeyError:
                    pass
                finally:
                    return similars_list
            else: return None
        # end inner_most_similar
        #
        matrix_of_similars = list(filter(
            None.__ne__,
            list(map(lambda token: inner_most_similar(token), tokens))
        ))
        #print(matrix_of_similars)
        """flatten the matrix and put all in a set to remove possible repetition
        then add the original tokens
        """
        similars_set = set(itertools.chain(*matrix_of_similars))
        similars_set.update(tokens)
        #print(similars_set)
        return similars_set
    # end 
    
    def __get_wordvectors_by_lang(self, lang: str):
        if (lang == 'en'):
            return self.english_wordvectors
        elif (lang == 'fr'):
            return self.french_wordvectors
        else:
            return None
    
    ##
    def __get_at_most_first_ten_formated_result(self, result):
        """
        Just returning a string madde of the title 
        and the description of the first ten result
        """
        """By default the first then are returned, so no need to use slice"""
        first_ten = list(map(lambda hit: hit['_source'], result['hits']['hits'][:10]))
        if(len(first_ten) == 0):
            return "NO SEARCH FOUND"
        else:
            return "\n".join(
                list(
                    map(
                        lambda res: f"{res['title']}\n{res['description']}\n{res['source_site_page_url']}\n\n", 
                        first_ten
                    )
                )
            )
    
    ##    
    def __plain_text_treatment(self, plain_text: str):
        """
        Proccess users request.
        Remove leading and tailing whte space and split the entry in tokens
        Return a list of tokens
        """
        # TODO add other treatment like remove punctuations
        return plain_text.lower().strip().split()
        
    ##
    def __detect_query_lang(self, text):
        """
        Detect the language of the user request so that we 
        call the according Word2Vec model for request enrichment
        """
        lang = detect(text)
        if(lang not in ['fr', 'en']):
            lang = 'en'
        return lang
# %%

# def main():
#     # =========================================================
#     # client = ElasticConnector().connect()
#     # my_searcher = Searcher()
    
#     # res = client.search(
#     #       index="users_feed_items",
#     #       body=a_body,
#     # )
#     # print(res['hits']['total'])
    
#     my_searcher = Searcher()
#     outout = my_searcher.search("virus")
#     print(outout)
    

# if __name__ == '__main__':
#     main()


# %%
