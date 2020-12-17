# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 15:12:15 2020

@author: Faroud
"""
"""Use to index a bunch of document :
Put JSON documents into ElasticSearch index    
"""

""" IMPORTANT
This is a script just to have an overview over all 
the different functionality that our final system 
should provide.
A final version well structured and working with all the other 
modules (RSS-Collector and the classifier) will be provided very soon.
"""

# %%
import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
helper_dir = data_dir = os.path.abspath(os.path.join(src_dir, '../helper'))
sys.path.append(src_dir)
sys.path.append(helper_dir)

data_dir = os.path.abspath(os.path.join(src_dir, '../../RSS_Collector/unlabeled_data/'))
ARTICLES_FILE_PATH = os.path.join(data_dir, 'articles')

# %%
from Indexer import Indexer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from ElasticConnector import ElasticConnector


import shelve
import json
import tqdm

# %%

class ItemIndexer(Indexer):
    index_name = "feed_items" # @property

    
    def create_index(self):
        """
        Creates an index in Elasticsearch if one doesn't already exist.
        """
        self.client.indices.create(
            index=self.index_name,
            body={
                "settings": {"number_of_shards": 1},
                "mappings": {
                    "properties": {
                        "hid": {"type": "keyword"},
                        "source_feed_url": {"type": "text"},
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "summary": {"type": "text"},
                        "language": {"type": "text"},
                        "date": {"type": "date"},
                        "content": {"type": "text"}
                    }
                },
            },
            ignore=400,
        )

    def delete_index(self):
        self.client.indices.delete(index=self.index_name, ignore=[400, 404])
        
    def index(self, hids=None):
        # first check if index already exists, if 
        if(not self.client.indices.exists(self.index_name)):
            # create the index
            self.create_index()
            # set hids to None: As the index doesn't exists we will index all the 
            # document in the local file so: no need to take those hids in account
            hids = None
        else: 
            pass
        print("Indexing doc...")
        
        nb_article_to_index = self.stats(hids)
        print("NB ARTICLE TO INDEX:", nb_article_to_index)
        #
        progress = tqdm.tqdm("articles", total=nb_article_to_index)
        successes = 0
        
        for ok, action in streaming_bulk(
            client=self.client, index=self.index_name, actions = self._generate_actions(hids)):
            progress.update(1)
            successes += ok
        print(f'Indexed {successes}/{nb_article_to_index}')
    

# %%


# %%
def main():
    # get connection
    client = ElasticConnector().connect()
    # create an ItemIndexer
    item_indexer = ItemIndexer(client, ARTICLES_FILE_PATH)
    # index documents
    item_indexer.index()
    
        

# %%
if __name__ == "__main__":
    main()

# %%

