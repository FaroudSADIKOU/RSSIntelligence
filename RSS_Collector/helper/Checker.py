# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 12:31:17 2020

@author: Faroud
"""
import os, inspect
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
import errno

#import time

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
crawling_settings_dir = data_dir = os.path.abspath(os.path.join(src_dir, '../crawling_settings'))
CRAWLING_SETTINGS_FILE_PATH = os.path.join(crawling_settings_dir, 'date_setting')

OFFSET= relativedelta(hours=12) # very important don't mess hour with hours. the s is import..
# %%

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

#
def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    
    mkdir_p(os.path.dirname(path))
    return open(path, 'wb+')


# %%
def can_launch_crawling():
    status = False
    try:
        with open(CRAWLING_SETTINGS_FILE_PATH, 'rb') as f:
            unpickler= pickle.Unpickler(f)
            last_date= unpickler.load()
        #
        if last_date:
            # check the offset, and ...
            date_now = datetime.now()
            supposed_ok_date = last_date + OFFSET
            if(supposed_ok_date <= date_now):
                status = True
    except FileNotFoundError:
        # file doesn't exist this mean we've never crawled befor, so set status to rue 
        # to say yes we can crawl now
        status = True   
    
    return status
#
def update_last_crawling_date():
      with safe_open_w(CRAWLING_SETTINGS_FILE_PATH) as f:
         pickler = pickle.Pickler(f, protocol=pickle.HIGHEST_PROTOCOL)
         pickler.dump(datetime.now())
#
     
 
# %%