
from .ui import getText
from .ui import askUser


class Configurable:

    def __init__(self, name):
        self.name = name

    def set_dir(self, name, default, prompt):
        return self._set_config_value('dirs', name, default, prompt)

    def get_alias(self, name):
        return self.get_value('alias', name)
        
    def set_alias(self, name, default, prompt):
        return self._set_config_value('alias', name, default, prompt)

    def get_flag(self, name, default=False):
        return self.get_value('flags', name, default=default)

    def set_flag(self, name, defaultno, prompt): 
        value = askUser(prompt, defaultno=defaultno, help=self._get_help_function(), title=self.name)
        set_value('flags', name, value)
        return value

    def _set_config_value(self, category, name, default, prompt):
        (s, r) = getText(prompt=prompt, default=default, help=self._get_help_function(), title=self.name)
        if r:
            self.set_value(category, name, s)
            return s
        else:
            return None

    def _get_help_function(self):
        return self.help if hasattr(self, 'help') else None
