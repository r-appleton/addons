# -*- coding: utf-8 -*-

import urllib
import re
import base64
import certifi
from bs4 import BeautifulSoup

class ParsedSource:
    
    def __init__(self, name):
        self.name = name

    def lookup(self, word):
        url = self.get_initial_url(urllib.parse.quote(word))
        try:
            datafile = self._get(url)
            try:
                result = self.get_data_format_and_url(word, datafile.read().decode('utf-8'))
                if result != None:
                    (format, url) = result
                    if url != None:
                        return (format, self._download(url))
                return None
            finally:
                datafile.close()
        except urllib.error.HTTPError as x:
            if x.code == 404:
                return None
            else:
                raise Exception(url +'\n' + str(x))

    def _get(self, url):
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
        request = urllib.request.Request(url, data=None, headers={'User-Agent': useragent})
        return urllib.request.urlopen(request, cafile=certifi.where())
        
    def _download(self, url):
        datafile = self._get(url)
        try:
            return datafile.read()
        finally:
            datafile.close()
 