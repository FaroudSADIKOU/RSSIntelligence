# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 15:49:30 2020

@author: Faroud
"""
# %% Imports
import pandas as pd
from enum import Enum
# %% Global definitions

LINE_ITEM_SEPARATOR = " "
HEADER_DICT = {'link': 'feed_link', 'lang': 'language', 'cat': 'category'}


# %%

class MonitoredFeedReader():
    def __init__(self, file_path_ = "../data/ListFluxRSS-v1_.csv") -> None:
        self.file_path = file_path_
        self.dataset = self._read()
    
    def _read(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path, sep=LINE_ITEM_SEPARATOR, 
                           skip_blank_lines=True)
    
    def retrieve_url_and_category(self) -> pd.DataFrame:
        return self.dataset[[HEADER_DICT['link'], HEADER_DICT['cat']]]
    




# if __name__ == '__main__':
#     mfr =  MonitoredFeedReader()
#     url_and_cat = mfr.retrieve_url_and_category()
#     print(url_and_cat)
    
    
    
    