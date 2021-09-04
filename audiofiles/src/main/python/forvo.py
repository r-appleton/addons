# -*- coding: utf-8 -*-

import re
import base64
from bs4 import BeautifulSoup
from .parsed_source import ParsedSource


class ForvoParser:
    def lookup(self, language, word, data):
        self._urls = []
        doc = BeautifulSoup(data, 'html.parser')
        self._get_javascript_values(doc)
        div = doc.find('div', id='language-container-{0}'.format(language))
        span = div.find('span', class_='play', title='Listen {0} pronunciation'.format(word))
        if not span:
            span = div.find('span', class_='play', title='Listen {0} pronunciation'.format(word.capitalize()))
        return self._parse_tag(span) if span else None

    def _get_javascript_values(self, doc):
        self._protocol = None
        self._server_host = None
        self._audio_host = None
        
        for script in doc.find_all('script', type='text/javascript'):
            if script.string != None:
                self._protocol = self._get_var_value('defaultProtocol', script.string, self._protocol)
                self._server_host = self._get_var_value('_SERVER_HOST', script.string, self._server_host)
                self._audio_host = self._get_var_value('_AUDIO_HTTP_HOST', script.string, self._audio_host)
    
    def _get_var_value(self, varname, script, dflt):
        if varname in script:
            m = re.search(r'var\s+{0}\s*=\s*\'(?P<value>.+?)\'\s*;'.format(varname), script)
            return m.group('value') if m else dflt
        else:
            return dflt
    
    def _parse_tag(self, tag):
        # word
        m = re.match(r'Play\(\d+,(?P<b>|\'.*?\'),(?P<c>|\'.*?\'),.*?,(?P<e>|\'.*?\'),(?P<f>|\'.*?\'),', tag.get('onclick'))
        if m:
            if self._server_host == self._audio_host:
                self._append(m, 'e', 'mp3', 'player-{0}-highHandler.php?path=')
                self._append(m, 'f', 'ogg', 'player-{0}-highHandler.php?path=')
                self._append(m, 'b', 'mp3', 'player-{0}Handler.php?path=')
                self._append(m, 'c', 'ogg', 'player-{0}Handler.php?path=')
            else:
                self._append(m, 'e', 'mp3', 'audios/{0}/')
                self._append(m, 'f', 'ogg', 'audios/{0}/')
                self._append(m, 'b', 'mp3', '{0}/')
                self._append(m, 'c', 'ogg', '{0}/')

        # phrase                
        m = re.match(r'PlayPhrase\(\d+,(?P<b>|\'.+?\'),(?P<c>|\'.+?\')', tag.get('onclick'))
        if m:
            if self._server_host == self._audio_host:
                self._append(m, 'b', 'mp3', 'player-phrasesMp3Handler.php?path=')
                self._append(m, 'c', 'ogg', 'player-phrasesOggHandler.php?path=')
            else:
                self._append(m, 'b', 'mp3', 'phrases/{0}/')
                self._append(m, 'c', 'ogg', 'phrases/{0}/')

        return self._urls[0] if len(self._urls) else None
        
    def _append(self, m, group, format, path):
        if m.group(group) not in ['', "''"]:
            data = base64.b64decode(m.group(group))
            path = path.format(format)
            url ='{0}//{1}/{2}{3}'.format(self._protocol, self._audio_host, path, data.decode('utf-8'))
            self._urls.append((format, url))


class Forvo(ParsedSource):
    def __init__(self):
        ParsedSource.__init__(self, 'Forvo')

    def setConfig(self, data):
        self._language = data['language'].lower()
    
    def get_initial_url(self, word):
        return 'https://forvo.com/word/{0}/#{1}'.format(word, self._language)
    
    def get_data_format_and_url(self, word, pagesource):
        return ForvoParser().lookup(self._language, word, pagesource)
