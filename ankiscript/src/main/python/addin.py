
import os.path
import re
import imp
import json
from aqt import mw
from aqt import addons
from .ui import askUser


class Addin:

    def __init__(self, name):
        self.name = name
        self._module = None

    def isInstalled(self):
        try:
            self._anki_module()
            return True
        except:
            return False

    def get_config(self):
        return mw.addonManager.getConfig(self._anki_module())

    def save_config(self, config):
        addon = self._anki_module()
        mw.addonManager.writeConfig(addon, config)

        # does the add-on define an action to be fired?
        act = mw.addonManager.configUpdatedAction(addon)
        if act:
            act(config)

    def install(self, id, course):
        # check, and ignore, if addin has already been installed
        if not self.isInstalled():
            # to prevent scam installations require user to authorise download
            # id must be looked up on Anki addin website and hardcoded in command file
            prompt = 'Install {0} add-in?\nUse Help to view add-in details'.format(self.name)
            help = 'https://ankiweb.net/shared/info/{0}'.format(id)
            if askUser(prompt, defaultno=True, help='https://ankiweb.net/shared/info/{0}'.format(id), title=course.name):
                from anki.httpclient import HttpClient
                (id, result) = addons.download_and_install_addon(mw.addonManager, HttpClient(), id)
                if isinstance(result, addons.DownloadError):
                    raise Exception('{0} download failed: {1}'.format(self.name, result)) 

    def configure(self, datasource, course, key=None):
        # NB. cannot update addins programmatically configured
        # key=None means replace whole config, else key is list of keys to traverse
        if key:
            config = self.get_config()
            d = config
            for k in key[:-1]:
                if k not in d:
                    raise Exception('"{0}" configuration does not contain key {1}'.format(self.name, '.'.join(key[:-1])))
                d = k[d]
            d[key[-1]] = self._get_addin_config_change(datasource, course)
            self.save_config(config)
        else:
            self.save_config(self._get_addin_config_change(datasource, course))

    def _get_addin_config_change(self, datasource, course):
        '''
        Load new config data and replace aliases with resolved values.
        '''
        filename = self.name.lower().replace(' ', '_')  + '.config'
        data = datasource.read(['config', 'addins'], filename)
        if not data:
            raise Exception('Cannot find new config data for ' + self.name)
            
        # simpler to replace ${alias} before converting string to json
        for alias in re.findall(r'\${(?P<alias>.*?)}', data):
            value = course.get_alias(alias)
            if value:
                data = data.replace('${' + alias + '}', value)
            
        return json.loads(data)

    def _anki_module(self):
        if self._module:
            return self._module
        else:
            for d in mw.addonManager.allAddons():
                if mw.addonManager.addonName(d) == self.name:
                    self._module = d
                    return self._module

            raise Exception('Cannot find {0} addin'.format(self.name))
        