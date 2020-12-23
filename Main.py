# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 19:22:07 2020

@author: Faroud
"""

"""
Main script to launch the framework

"""

# %% imports

import concurrent.futures

import os, sys, inspect

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(src_dir)


from RSS_Collector.Collector import Collector
from Indexer_Searcher.Searcher.Searcher import Searcher
# %%
  
def collect():
    """ Launches the RSSCollector module.
    At end the module call the indexer module to index 
    the new crawled data.
    """
    collector = Collector()
    collector.collect()

# %%
def launch_search():
    """ Launches the Searcher module.
    This is an interface between th users request and the elasticsearch index.
    """
    searcher = Searcher()
    searcher.launch()

# %%
def main():
    """ main function.
    Create two task and launch them.
    """
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(launch_search)
        executor.submit(collect)
       
# %%
if __name__ == '__main__':
    main()
    
#%%    