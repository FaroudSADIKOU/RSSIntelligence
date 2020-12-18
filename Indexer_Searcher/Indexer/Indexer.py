# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 15:09:26 2020

@author: Faroud
"""
# %% Imports 

import sys, os, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))

helper_dir = os.path.abspath(os.path.join(src_dir, '../helper'))
sys.path.append(helper_dir)

from DateTimeEncoder import DateTimeEncoder
from elasticsearch import Elasticsearch

import shelve
import json

# %%


from abc import ABC, abstractmethod

class Indexer(ABC):
    def __init__(self, client, data_to_index_file_path):
        self.client = client
        self.data_to_index_file_path = data_to_index_file_path
        
    @property
    @abstractmethod
    def index_name(self):
        pass
    
    ##
    def _generate_actions(self, hids=None):
        """
        Read the articles file and for each element, yields a single document.
        The function will be passed into bulk() to index many document in saquence.
        But if hids is not None, 
        Read the articles file and for the article with the hid in 
        the hids, yields a single document.
        
        """
        if hids is None:
            with shelve.open(self.data_to_index_file_path) as db:
                for key in db:
                    yield json.dumps(db[key], cls=DateTimeEncoder)
                
        else:
            with shelve.open(self.data_to_index_file_path) as db:
                for hid in hids:
                    try:
                        yield json.dumps(db[hid], cls=DateTimeEncoder)
                    except KeyError:
                        print(f'key {hid} not in db')
    ##
    def stats(self, hids):
        nb_items_to_index = 0
        if(hids is None):
            # open the articles database and return the nulber of articles inside
            with shelve.open(self.data_to_index_file_path) as db:
                nb_items_to_index = len(db)
        else:
            nb_items_to_index = len(hids)
        
        return nb_items_to_index
    
    ##
    @abstractmethod
    def index(self, hids=None):
        pass

    @abstractmethod
    def create_index(self):
        pass
    
    @abstractmethod
    def delete_index(self):
        pass
    
            
    