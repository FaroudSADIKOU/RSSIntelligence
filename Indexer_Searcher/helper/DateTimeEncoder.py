# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 15:57:32 2020

@author: Faroud
"""
"""
Subclass of jSONEncoder to serialize DateTime into JSN
"""

# %% imports
import json
import datetime
# %%

class DateTimeEncoder(json.JSONEncoder):
    
    def default(self, obj):
        """
        Override the default() method of a JSONEncoder Class, 
        where we can convert DateTime value into ISO format 
        so it can be serialized. 
        """
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()