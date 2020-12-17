# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 11:29:52 2020

@author: Faroud
"""

# %% Imports 
import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))

data_dir = os.path.abspath(os.path.join(src_dir, 'unlabeled_data/'))
PLAIN_FEED_URL_FILE_PATH = os.path.join(data_dir, 'ListFluxRSS-v1_.csv')
MONITORED_FEED_FILE_PATH = os.path.join(data_dir, 'monitored_feeds')
ARTICLES_FILE_PATH = os.path.join(data_dir, 'articles')

sys.path.append(src_dir)

import feedparser
from bs4 import BeautifulSoup

from langdetect import detect, lang_detect_exception


import shelve
from dateutil import parser as du_parser
from tqdm import tqdm
import numpy as np
import threading
import concurrent.futures
from concurrent.futures import as_completed


from os.path import getmtime

from model.Feed import Feed
from model import FeedItem
from helper import Helpers, MonitoredFeedReader as mfr
import SimpleCrawler



# %%

crawler = SimpleCrawler.SimpleCrawler()

# lock definition
threadLock = threading.Lock()

#%% 
"""
"""

class SimpleFeedParser():
    def __init__(self, plain_feeds_data_path, monitored_feeds_data_path, articles_data_path):
        self.plain_feeds_data_path = plain_feeds_data_path
        self.monitored_feeds_data_path = monitored_feeds_data_path
        self.articles_data_path = articles_data_path    
    
    #
    def parseFeeds_from_url_in_file(self):
        """
        Use to parse a bunch of Feed. Read the file containing the 
        different feeds information and yield a genarator of Feed element 
        so that we can map the method parsing one feed to it.
        """
        status = False
        def generate_feeds_to_parse(database):
            #go through all the registered fedds url
            #print("[URLS]: \n")
            for key in database:
                url = database[key]['url']
                etag = database[key]['etag']
                last_modified_date = database[key]['last_modified']
                pub_date = database[key]['pub_date']
                
                yield Feed(url, None, etag, last_modified_date, pub_date)
        ##
        
        #First preproccess
        if(not self.__preproccessing()):
            print(f"""PLEASE ADD THE FILE: {self.plain_feeds_data_path} AND RETRY AGAIN. 
                  OR TRY TO USE parseFeed METHOD BY GIVING A URL IN ARGUMENT""")
        else:
            new_item_hids = [] # will contain the hid of the new crawled item
            with shelve.open(self.monitored_feeds_data_path, writeback=True) as database:
                feeds_to_parse = generate_feeds_to_parse(database) # return a genertor
                # multi proccess area
                with tqdm(total=self.stats_monitored_feeds()) as pbar:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                        futures_new_items_hids = [executor.submit(self.parseFeed, feed) for feed in feeds_to_parse]
                        
                        for future_item_hid in as_completed(futures_new_items_hids):
                            pbar.update(1)
                            new_item_hids = np.append(new_item_hids, future_item_hid.result())
                            
                # close database once all the thread joined
                #database.close
            status = True #important
        print("END OF PARSING RETURN...")
        return status, new_item_hids

    
    ###
    def parseFeed(self, feed: Feed):  
        """
        parse a feed from a url and retrieve some useful items 
        for our use case.

        Parameters
        ----------
        url : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        new_items_hid_collector = [] # will keep the hids of the new article saved to file
        #print('[URL TO PARSE]: {}'.format(feed.url))
        feed_data = feedparser.parse(feed.url, etag=feed.etag, modified=feed.modif_date)
        if(not self.__isOkStatus(feed_data.get("status"))): #no mofication since last time
            #print("\tNo modification since last time")
            return []
        else:
            # this case means two things:
                # the feed provider doesn't support etag or lmd so we got to implment something ourself
                # there is an update (a modification since the lmd)
            local_pub_date_str = feed.pub_date
            pub_date_str = feed_data.feed.get('published', local_pub_date_str)
            
            if(not self.__is_pubDate_after(pub_date_str, local_pub_date_str)):
                #print("\tNo modification since last time")
                return []
            else:
                #check if the feed is well formed
                if not self.__isFeed_WellFormed(feed_data.bozo):
                    #print("\tBad Feed Formation skipping feed ...")
                    return []
                else: 
                    #print("\tFeed is well formed")
                    #get the other elements not always in a feed
                    for item in feed_data.entries: #go through the items in the feed
                        a_feed_item = self.__item_content_getter(item, feed)
                        if (a_feed_item is not None):
                            #Time to save into media file
                            if (self.__save_article_to_file(a_feed_item)):
                                # add the saved article to the collector
                                new_items_hid_collector.append(a_feed_item.hid) 
                    # update feeds header informations in local database
                    self.__update_local_feed_header(feed, feed_data)
                    return new_items_hid_collector
     
        
     ###
    def __item_content_getter(self, item, feed):
        #print("Inside content getter")
        if ('title' not in item):
            return None
        else:
            source_feed_url = feed.url
            title = item.title
            source_site_url = item.get('link', None)
            description = item.get('description', None)
            summary = item.get('summary', None)
            #According to the RSS 2.0 DTD, there must be at least 
            #one <title> or <description> in an item and the rest of the tags is optional.
            if(description is None and summary is None) or (not description and not summary):
                return None
            else:
                summary = self.__pretiffy(summary)
                description = self.__pretiffy(description)
                #make the id with the above data
                hid = Helpers.build_id_from_str(source_feed_url + title + source_site_url + description)
                # use sum. or descrp. or title to detect language
                language =  self.__langDetectExtend(summary, description, title)
                #language = detect(summary) if description is None or not description else detect(description)
                #
                date = self.__getDate(item)
                #print(date)
                #
                content = crawler.parse(source_site_url)
                
                if content == '':
                    #print("Out of content getter")
                    return None
                else:
                    #create a FeedItem fill of the retrieved informations.
                    #print("Out of content getter")
                    # get a category for the content by our model
                    return FeedItem.FeedItem(hid, 
                                             source_feed_url, source_site_url, 
                                             title, description, summary, 
                                             language, date, content, category )
    

    ###
    def stats(self):
        """
        Returns the number of rss item we have in total in our database
        """
        # open the articles database and return the nulber of articles inside
        with shelve.open(self.articles_data_path) as db:
            return len(db)
        
    def stats_monitored_feeds(self):
        """
        Returns the number of Feed we are monitoring
        """
        # open the articles database and return the nulber of articles inside
        with shelve.open(self.monitored_feeds_data_path) as db:
            return len(db)

    def __pretiffy(self, markup):
        """
        Arround some item fields, there is still some tag. 
        Like <p> <p/> arond the title content.
        Parameters
        ----------
        markup : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return BeautifulSoup(markup, 'html.parser').get_text() if markup is not None else None


    ###
    def __isOkStatus(self, status):  
        """
        """
        if(status == 200):
            return True
        elif(status == 304): # No modification
            #print("\tNo modification since last time")
            pass
        elif(status == 301): # feed was permanently redirected to a new URL
            pass
        elif(status == None or status == 410): # bad feed or feed is gone, delete url from database
            #TODO act code for deletion here
            pass
        return False
    
    ###
    def __is_pubDate_after(self, pub_date_str: str, local_pub_date_str: str):
        """
        Compares two date 
        """
        # pay attention to the if conditions orser, it's important
        if not local_pub_date_str:
            return True
        elif not pub_date_str:
            return False
        else:
            pub_date = du_parser.parse(pub_date_str)
            local_pub_date = du_parser.parse(local_pub_date_str)
            
            return pub_date > local_pub_date
    
    
    #TODO Add an implementation.
    def __langDetectExtend(self, *text_args):
        #print("/".join(text_args))
        """
    
        Parameters
        ----------
        list_of_text : TYPE
            DESCRIPTION.
    
        Returns
        -------
        str
            DESCRIPTION.
    
        """
        text_supposed_not_none = next((text for text in text_args if text), '')
        lang = 'UKNOWN'
        try:
            lang = detect(text_supposed_not_none)
        except lang_detect_exception.LangDetectException:
            pass
            print('problem detecting language, set to UNKNOWN')
            
        return lang
        #return None if (text_supposed_not_none is None) else detect(text_supposed_not_none)
        


    def __getDate(self, item):
        """
    
        """
        date = item.get('published', None)
        return None if not date else du_parser.parse(date)
    
    def __isFeed_WellFormed(self, bozo):
        return bozo == 0
       

    ###
    # ask for lock inside there
    def __save_article_to_file(self, article_: FeedItem):
        save_status = False
        hid = article_.hid
        # acquire the lock
        threadLock.acquire()
        database = shelve.open(self.articles_data_path)
        # first check if the database contain that key
        if hid in database:
            #print("\tArticle already exists")
            database.close()
        else:
            #print("\t[SAVE ARTICLE TO FILE]")
            # this article is new, so save it
            try:
                database[hid] = vars(article_)
                save_status = True
            finally:
                database.close()
        # release the lock
        threadLock.release()
        return save_status
    
    
    ###
    def __build_feed_key(self, feed: Feed):
        """
        """
        return Helpers.build_id_from_str(str(feed))
    
    def __update_local_feed_header(self, feed: Feed, feed_data):
        # acquire the lock
        threadLock.acquire()
        database = shelve.open(self.monitored_feeds_data_path)
        key = self.__build_feed_key(feed)
        try:
            feed_record = database[key]
            try:  
                feed_record['etag'] = feed_data.etag
            except AttributeError :
                pass
                #print("Attribut etag doesn't exist")
            try:
                feed_record['last_modified'] = feed_data.modified
            except AttributeError:
                pass
                #print("Attribut modified doesn't exist")
            try:
                feed_record['pub_date'] = feed_data.feed.published
            except AttributeError:
                pass
                #print("Attribut pubDate doesn't exist")
            database[key] = feed_record
        except KeyError:
            pass
            #print(f"A problem with key: {KeyError}")
        finally:
            database.close()
        # release the lock
        threadLock.release()
    
# %%
    def __preproccessing(self):
        #
        def setting_up():
            monitored_feed_reader = mfr.MonitoredFeedReader(self.plain_feeds_data_path)
            # the following set contain url and category and features
            moniored_feeds_dataset = monitored_feed_reader.retrieve_url()
                    
            #Get the actual monitored feed url and check if they are all taken into account
            database = shelve.open(self.monitored_feeds_data_path, writeback=True)
            #
            try: 
                for url in moniored_feeds_dataset['feed_link']:
                    a_feed = Feed(url, None)
                    key = self.__build_feed_key(a_feed)
                    if key in database:
                        pass
                        #print("exists")
                        #a_record = database[key]
                        #print('\t[etag = {} and last_modified={}]'.format(a_record['etag'], a_record['last_modified']))
                    else: 
                        #add to database
                        database[key] = {'url': url,
                                         'etag': '', 'last_modified': '', 'pub_date': '' }
            finally:
                database.close()
        # end of setting_up()
        
        status = True
        print("[Preprocessing]: Start")
        # first compare the last modification date of the plain and the binary file
        try:
            plain_modif_date = getmtime(self.plain_feeds_data_path)
            try:
                binary_modif_date = getmtime(self.monitored_feeds_data_path+'.dat')
                if(plain_modif_date < binary_modif_date):
                    pass
                else:
                    setting_up()
                print("[Preprocessing]: Done")
            except FileNotFoundError:
                print(f"file {self.monitored_feeds_data_path} doesn't exist yet. [CREATION] ")
                setting_up()
            #
        except FileNotFoundError:
            print("No plain file found. Stoping preprocessing!")
            status = False
        
        return status

# %%


# def main():
#     simple_feed_parser = SimpleFeedParser(PLAIN_FEED_URL_FILE_PATH, 
#                                           MONITORED_FEED_FILE_PATH, 
#                                           ARTICLES_FILE_PATH)
    
#     simple_feed_parser.parseFeed("http://rss.cnn.com/rss/edition_world.rss")
#     #simple_feed_parser.testing_etags("http://rss.cnn.com/rss/edition_world.rss")
    
#     #simple_feed_parser.parseFeeds_from_url_in_file()
    
# if __name__ == '__main__':
#     main()

# %%
# import feedparser
# import dateutil.parser as dp
# fdd = feedparser.parse("http://rss.cnn.com/rss/edition_world.rss")
# date = fdd.entries[0].get("published", None)

# #print(fdd.entries[0])
# print(type(date))
# print(date)

# parsed_date = dp.parse(None)

#%% 
# text_args = ['', 'aaaaa', "what is that"]
# not_empty_text = next((text for text in text_args if text), "EMPTY")
# print(not_empty_text)


