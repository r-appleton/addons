# -*- coding: utf-8 -*-

import html
from .parsed_source import ParsedSource


class WiktionaryParser(html.parser.HTMLParser):

    def handle_starttag(self, tag, attributes):
        if not self._url and tag == 'a' and self._attribute(attributes, 'title') == self._title:
            self._url = self._attribute(attributes, 'href')

    def lookup(self, title, data):
        self._title = title
        self._url = None
        try:
            self.feed(data)
            return self._url
        finally:
            self.close()

    def _attribute(self, attributes, name):
        for (attr, value) in attributes:
            if attr == name:
                return value
        return None


class Wiktionary(ParsedSource):
    def __init__(self):
        ParsedSource.__init__(self, 'Wiktionary')
        self._format = 'ogg'

    def setConfig(self, data):
        self._locale = data['locale'].capitalize()
    
    def get_initial_url(self, word):
        return 'https://commons.wikimedia.org/wiki/File:{0}'.format(self._title(word))
    
    def get_data_format_and_url(self, word, pagesource):
        url = WiktionaryParser().lookup(self._title(word), pagesource)
        return (self._format, url) if url else None

    def _title(self, word):
        return '{0}-{1}.{2}'.format(self._locale, word, self._format)
