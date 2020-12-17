# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 22:04:08 2020

@author: Faroud
"""
import http.client

import requests
#from urllib import request
#from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

# %% 

class SimpleCrawler:

    def getPage(self, url):
        """Get a page source content based on its url.
        
        Parameters
        ----------
        url: str 
            A source page url.
        """
        try:
            html = requests.get(url)
        except requests.exceptions.ConnectionError:
            print("DNS failure, refused connection")
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print("Retry")
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print("BAD URL")
        except HTTPError:
            print("an HTTPERROR occured")
            return None
        except URLError:
            print('The server could not be found!')
            return None
        except http.client.RemoteDisconnected:
            print("http client Remote disconnected")
            return None
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print("Catastrophe")
            raise SystemExit(e)
        except:
            print("An unknown problem occured during crawling")
        else:
            bs = BeautifulSoup(html.text, 'html.parser')
            return bs
     
    
    def  getAContent(self, pageObject, selector):
        """
        Used to get a content  string from  a Beautiful Soup 
        object and a selector
        
        Parameters
        ----------
        pageObject : BeautifulSoup
            A BeautifulSoup object .
        selector : str
            A Valid CSS Selector.

        Returns
        -------
        str
            A Unicode text or empty string if no object is found 
            for the given selector.

        """
        selectedElements = pageObject.select(selector)
        if selectedElements is not None and len(selectedElements) > 0:
            return '\n'.join( [ anElement.get_text() for anElement in selectedElements ] )
        return ''

    def parse(self, url):
        """
        Extract the needed content from a Website based on a giving url
        
        Parameters
        ----------
        url : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        """
        #cal getPage method to get if possible a BeautifulSoup object
        bs = self.getPage(url)
        if bs is not None:
            title = self.getAContent(bs, tags['title'])
            #TODO clean the title
            #print("\n[TITLE] : \n", title)
            """can not use the same getAContent function to get the body here.
            There is some extra proccessing needed.
            """
            body = bs.body
            #print("\n\n\n[Received] body to clean: \n", body )
            cleaned_body = self.extractContentFromBody(body)
            #print("\n[CLEANED BODY]: \n", cleaned_body)
            #A webpage should either have a title or a a body
            if title != '' or cleaned_body != '':
                return f'{title} {cleaned_body}'
            return ''
        return ''
    def extractContentFromBody(self, body_bs_object):
        #list of tags to remove
        tags_to_remove = ['header', 'footer','script', 'style', 'a', 'table', 'img', 'form', 'iframe' ]
        for tag in tags_to_remove:
            try:
                for element in body_bs_object.find_all(tag):
                    element.decompose() #remove footer
            except AttributeError:
                pass
        #TODO can use soupStrainer
        """
        for string in body_bs_object.stripped_strings:
            print(repr(string))
        return '\n'.join( [repr(string) for string in body_bs_object.stripped_strings] )
        """
        return body_bs_object.get_text(" ",strip=True)


#TODO remove from this file
"""
Define som tag,
For example the tag inside a HTML doc from wich we can get 
    -the title
    -the body
    - ...
"""
tags = {'title' : 'h1',
        'body' : 'body.div'}


# %%
#TODO To remove
# """QUICK TESTING"""
# crawler = SimpleCrawler()
# parsed_text = crawler.parse("https://rmcsport.bfmtv.com/football/equipe-de-france-henry-doit-elle-son-retour-a-une-petite-phrase-de-le-graet-2007975.html")
# print(parsed_text)
