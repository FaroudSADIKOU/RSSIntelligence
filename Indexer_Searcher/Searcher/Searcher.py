# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 19:21:22 2020

@author: Faroud
"""
# %% imports
import os, sys, inspect
import PySimpleGUI as sg

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
helper_dir = os.path.join(src_dir, "../helper")
sys.path.append(helper_dir)

from ElasticConnector import ElasticConnector
# %%
class Searcher(): #ItemSearcher
    def __init__(self):
        self.client = ElasticConnector().connect()
        self.index_name = "feed_items"
    
    def launch(self):
        # All the stuff inside the window.
        layout = [  
            [sg.Text('SEARCHER', size=(100, 1), justification='center')],
            [sg.InputText(), sg.Button('search')] ,
            [sg.Multiline(size=(80, 20), key='-OUTPUT-')]
        ]
        
        # Create the Window
        window = sg.Window('SEARCHER', layout, size=(500, 300), element_justification='c')
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
        result_to_send = ""
        # check server availability
        if(self.client.ping()):
            res = self.client.search(
                index=self.index_name,
                body={
                    'query':{
                        'match':{
                            "description":self.__plain_text_treatment(plain_text)
                        }
                    }
                }
            )
            #
            result_to_send = self.__get_at_most_first_ten_formated_result(res)
        else:
            result_to_send = "COULD NOT REACH SERVER"
        return result_to_send
    
    ##
    def __get_at_most_first_ten_formated_result(self, result):
        """
        Just returning a string madde of the title 
        and the description of the first ten result
        """
        """By default the first then are returned, so no need to use slice"""
        first_ten = list(map(lambda hit: hit['_source'], result['hits']['hits'][:10]))
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
        # TODO add other treatment
        return plain_text.strip()
        
        
# %%
# client = ElasticConnector().connect()
# my_searcher = Searcher()

# print(my_searcher.search("lucky"))
