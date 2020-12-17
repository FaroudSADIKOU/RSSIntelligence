# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 20:23:17 2020

@author: Faroud

Test class for SimpleCrawler Class.
"""
import sys
sys.path.append('..')

import unittest

from SimpleCrawler import SimpleCrawler
import bs4

crawler = SimpleCrawler()
class SimpleCrawlerTest(unittest.TestCase):

    url_list = [
        "https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html?highlight=navigablestring", 
        "https://docs.python.org/fr/3/library/urllib.request.html#module-urllib.request",
        "https://pythonpedia.com/en/tutorial/10629/shelve",
        "https://textract.readthedocs.io/en/v1.6.1/python_package.html",
        "https://thisIsAUrlThatShouldNotExist_It_is_used_forTestPurpose.html",
        "https://kotlinlang.org/",
        "https://edition.cnn.com/2020/09/22/tennis/original-9-wta-tennis-cmd-spt-intl/index.html"
        ]
    
    def test_get_page(self):
        """

        Returns
        -------
        None.

        """
        returned_content_s_type = [ isinstance( crawler.getPage(url), bs4.BeautifulSoup) for url in self.url_list  ]
        self.assertEqual(returned_content_s_type, [True, True, True, False, False, True, True])
        
    def test_get_a_content(self):
        crawler.parse(self.url_list[6])
        

if __name__ == '__main__':
    unittest.main()
