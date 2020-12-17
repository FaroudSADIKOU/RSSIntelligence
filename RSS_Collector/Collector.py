# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 12:26:56 2020

@author: Faroud
"""

# %%
import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(src_dir)

data_dir = os.path.abspath(os.path.join(src_dir, 'data/'))

PLAIN_FEED_URL_FILE_PATH = os.path.join(data_dir, 'ListFluxRSS-v1_.csv')
MONITORED_FEED_FILE_PATH = os.path.join(data_dir, 'monitored_feeds')
ARTICLES_FILE_PATH = os.path.join(data_dir, 'articles')

# PLAIN_FEED_URL_FILE_PATH = os.path.join(data_dir, 'ListFluxRSS-v1__test.csv')
# MONITORED_FEED_FILE_PATH = os.path.join(data_dir, 'monitored_feeds__test')
# ARTICLES_FILE_PATH = os.path.join(data_dir, 'articles__test')

from helper import Checker
from SimpleFeedParser import SimpleFeedParser

indexer_searcher_dir = os.path.abspath(os.path.join(src_dir, '..'))
sys.path.append(indexer_searcher_dir)
from Indexer_Searcher.helper.ElasticConnector import ElasticConnector
from Indexer_Searcher.Indexer.ItemIndexer import ItemIndexer

#from elasticsearch import Elasticsearch
# %%
class Collector():
    def __init__(self):
        pass
    
    def collect(self):
        if(Checker.can_launch_crawling()):
            print("GO CRAWL NEW ARTICLES\n")
            simple_feed_parser = SimpleFeedParser(PLAIN_FEED_URL_FILE_PATH, MONITORED_FEED_FILE_PATH, ARTICLES_FILE_PATH)
            #
            crawl_status, new_articles_hid_list = simple_feed_parser.parseFeeds_from_url_in_file()
            print(crawl_status)
            nb_new_articles = len(new_articles_hid_list)
            print(f'New article: {nb_new_articles}')
            #  quick check: stat on the existing docs
            print(f'Total article in file: {simple_feed_parser.stats()}')
            
            if(nb_new_articles > 0):
                client = ElasticConnector().connect()  # get connection
                if client.ping():
                    # create an ItemIndexer
                    item_indexer = ItemIndexer(client, ARTICLES_FILE_PATH)
                    # index documents
                    item_indexer.index(new_articles_hid_list)
                else:
                    print("New document not indexed, cauze server unavailable")
            #update the last crawl time
            if crawl_status:
                Checker.update_last_crawling_date()
        else:
            print("NO NEED TO CRAWL NEW ARTICLES FOR NOW")