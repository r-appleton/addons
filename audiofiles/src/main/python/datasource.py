# -*- coding: utf-8 -*-

import tempfile
import uuid
from aqt.utils import showWarning
from .wiktionary import Wiktionary
from .openrussian import OpenRussian
from .forvo import Forvo


class Datasource:
    def __init__(self):
        self._dir = None
        self._use_random_filename = None
        self.use_text_selection = False
        # source precedence is the order in this list
        self._sources = [OpenRussian(), Wiktionary(), Forvo()]
    
    def setConfig(self, data):
        self._dir = data['dir'] if 'dir' in data and data['dir'] != '' else tempfile.gettempdir() 
        self._use_random_filename = 'filenames' in data and data['filenames'].lower() == 'random'
        self.use_text_selection = data['use_selection'] if 'use_selection' in data else False

        for source in self._sources:
            settings = data['sources'][source.name]
            if settings:
                source.enabled = settings['enabled']
                source.setConfig(settings)
            else:
                source.enabled = False
    
    def lookup(self, word):
        for source in self._sources:
            if source.enabled:
                try:
                    result = source.lookup(word)
                    if result != None:
                        (fmt, data) = result
                        if data != None:
                            return self._save(word, data, fmt)
                except Exception as x:
                    showWarning('Error finding sound data for {0} from {1}:\n{2}'.format(word, source.name, str(x)), title='Sound Files')
        return None
    
    def _save(self, word, data, fmt):
        basename = str(uuid.uuid1()) if self._use_random_filename else word
        filename = '{0}/{1}.{2}'.format(self._dir, basename, fmt)
        with open(filename, 'wb') as f:
            f.write(data)
        return filename
