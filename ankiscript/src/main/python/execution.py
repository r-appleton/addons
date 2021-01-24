
from .configurable import Configurable


class AdHocExecution(Configurable):

    def __init__(self, name = 'Ad-hoc script'):
        Configurable.__init__(self, name)
        self._config = {'flags':{}, 'dirs':{}, 'alias':{}}

    def get_value(self, category, name, default=None):
        # exception for undefined category OK as parser catches exception and reverts updates
        return self._config[category][name] if name in self._config[category] else default
    
    def set_value(self, category, name, value):
        self._config[category][name] = value
