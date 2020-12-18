# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 19:22:07 2020

@author: Faroud
"""

# %% imports

import concurrent.futures

import os, sys, inspect

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(src_dir)

# from RSS_Collector.SimpleFeedParser import SimpleFeedParser
# from RSS_Collector.helper import Checker

# data_dir = os.path.abspath(os.path.join(src_dir, 'RSS_Collector/data'))
# PLAIN_FEED_URL_FILE_PATH = os.path.join(data_dir, 'ListFluxRSS-v1__test.csv')
# MONITORED_FEED_FILE_PATH = os.path.join(data_dir, 'monitored_feeds__test')
# ARTICLES_FILE_PATH = os.path.join(data_dir, 'articles__test')

# from Indexer_Searcher.helper.ElasticConnector import ElasticConnector
# from Indexer_Searcher.Indexer.ItemIndexer import ItemIndexer

from RSS_Collector.Collector import Collector
from Indexer_Searcher.Searcher.Searcher import Searcher
# %%
  
def collect():
    collector = Collector()
    collector.collect()

# %%
def launch_search():
    searcher = Searcher()
    searcher.launch()

# %%
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(launch_search)
        executor.submit(collect)
        #future_search = executor.submit(launch_search)
        
        # while True:
        #     if(future_search.done()):
        #         print("\n\nSEARCH DONE .... \n\n")
        #         break;

# %%
if __name__ == '__main__':
    main()
    
#%%    