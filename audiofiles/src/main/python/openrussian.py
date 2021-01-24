# -*- coding: utf-8 -*-

import urllib
import certifi


class OpenRussian:
    
    def __init__(self):
        self.name = 'Open Russian'
        self._url = 'https://openrussian.org/audio-shtooka/{0}.mp3'
        self._format = 'mp3'

    def setConfig(self, data):
        pass
    
    def lookup(self, word):
        url = self._url.format(urllib.parse.quote(word))
        try:
            datafile = urllib.request.urlopen(url, cafile=certifi.where())
            try:
                return (self._format, datafile.read())
            finally:
                datafile.close()
        except urllib.error.HTTPError as x:
            if x.code == 404:
                return None
            else:
                raise x
        