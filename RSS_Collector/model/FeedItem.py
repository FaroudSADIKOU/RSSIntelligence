# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 19:48:20 2020

@author: Faroud
"""

"""
We need a Feed to have the following informations

"""
import datetime
class FeedItem(object):
    def __init__(self,
             hid_, 
             source_feed_url_, source_site_page_url_,
             title_, description_, summary_,
             language_, 
             date_: datetime.datetime,
             content_, predicted_category_):
        self.hid = hid_
        self.source_feed_url = source_feed_url_
        self.source_site_page_url = source_site_page_url_
        self.title = title_
        self.description = description_
        self.summary = summary_
        self.language = language_
        self.date = date_
        self.content = content_
        self.predicted_category = predicted_category_
 
    def __str__(self):
        return '[HID]:\n {} \n[TITLE]:\n {} \n[SITE_URL]:\n {} \n[CONTENT]:\n {}'.format(
            self.hid, self.title, self.source_site_page_url, self.content)

# %% TESTING

# if __name__ == '__main__':
#     feed_item  = FeedItem(1, 'url_feed', 'url_site', 'a_title', 'a_description', 'a_summary', 'fr', 'date', 'CONTENT')
