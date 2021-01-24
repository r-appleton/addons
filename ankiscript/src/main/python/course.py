
import os.path
import json
from aqt import mw
from aqt.utils import showInfo, showWarning, openLink
from .addin import Addin
from .parser import Parser
from .configurable import Configurable


class Course(Configurable):

    def __init__(self, name, help=None, nosetup=False, syntax=None):
        '''
        name    - course name for end user, also used as Anki module name
        help    - either a path to the dir containing help files, or a (dir, main help page name) tuple
        nosetup - if True course does not require any initial setup to be run by the user
        '''
        Configurable.__init__(self, name)
        self._course = Addin(name)
        self._help = (help, 'index.html') if isinstance(help, str) else help
        self._syntax = syntax
        
        # mark as setup if no initialization is required
        if nosetup:
            self.set_value('flags', 'setup', True)

    def help(self, page=None):
        if self._help:
            openLink('file:///' + os.path.join(self._help[0], page if page else self._help[1]))

    def isSetup(self):
        return self.get_flag('setup', default=False)
        
    def setup(self, source):
        if self.isSetup():
            showInfo('Ignored, as {0} has already been setup'.format(self.name), title=self.name)
        else:
            status = self._update(source, 'setup') if isinstance(source, str) else source(self)
            if status:
                self.set_value('flags', 'setup', True)

    def upload(self, source, description=None):
        if self.isSetup():
            return self._update(source, description)
        else:
            showInfo('Ignored, as {0} has not been setup'.format(self.name), title=self.name)
            return False

    def get_value(self, category, name, default=None):
        config = self._config()
        
        # exception for undefined category OK as parser catches exception and reverts updates
        return config[category][name] if name in config[category] else default
    
    def set_value(self, category, name, value):
        config = self._config()
        config[category][name] = value
        self._course.save_config(config)

    def _config(self):
        config = self._course.get_config()
        
        if not config:
            config = {'flags':{}, 'dirs':{}, 'alias':{}}

            d = mw.addonManager.addonsFolder(self._course._anki_module())
            path = os.path.join(d, "config.json")
            with open(path, 'w', encoding="utf8") as f:
                json.dump(config, f)

        return config

    def _update(self, source, description=None):
        return Parser.parse(source, self, syntax=self._syntax, description=description)
