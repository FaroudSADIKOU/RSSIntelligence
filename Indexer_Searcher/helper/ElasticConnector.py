# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 20:31:39 2020

@author: Faroud
"""


# %% imports
from elasticsearch import Elasticsearch
 

# %%
"""
Use to get one instance of the Elasticsearch client.
The Singleton pattern design is implemented here
"""
class ElasticConnector(object):
    __instance = None # keep instance reference
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.__connection = None
        return cls.__instance
    
    def connect(self):
        """
        Create an instance of ElasticSearch if it does'nt already exists, 
        otherwise, return the existing one.
        """
        if not self.__connection:
            print("Etablishing conection...")
            self.__connection = Elasticsearch(['localhost'], port=9200)
        if self.__connection.ping():
            print('Connected')
        else:
            print('Could not connect!')
        return self.__connection

# %%
# e1 = ElasticConnector()
# print(e1)
# es1 = e1.connect()
# print(id(es1))

# e2 = ElasticConnector()
# print(e2)
# es2 = e1.connect()
# print(id(es2))





