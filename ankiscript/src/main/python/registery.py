
import re
import inspect


class CommandRegistery:
    @staticmethod
    def find():
        return registery

    def __init__(self):
        self._callbacks = {}

    def register(self, regexp, f):
        self._callbacks[regexp] = {}
        self._callbacks[regexp]['pattern'] = re.compile(regexp)
        self._callbacks[regexp]['function'] = f
        self._callbacks[regexp]['args'] = inspect.getargspec(f).args

    def parse(self, line, **kwargs):
        for regexp in self._callbacks.keys():
            m = self._callbacks[regexp]['pattern'].match(line)
            if m:
                args = [m[arg] for arg in self._callbacks[regexp]['args']]
                self._callbacks[regexp]['function'](*args, **kwargs)
                return True

        return False


registery = CommandRegistery()
