
import re
from .registery import CommandRegistery


class command(object):
        
    def __init__(self, regexp):
        # ensure that regexp matches the whole input line
        self.regexp = regexp + '$'
    
    def __call__(self, f):
        def decorated(args):
            f(*args)
            
        regexp = self.regexp
        regexp = regexp.replace('(', '\(')
        regexp = regexp.replace(')', '\)')
        regexp = regexp.replace('[', '\[')
        regexp = regexp.replace(']', '\]')
        
        for m in re.finditer(r'{(?P<var>\w+?)}', self.regexp):
            s = m.group(0)
            regexp = regexp.replace(s, '(?P<{0}>.*)'.format(s[1:-1]))
        
        CommandRegistery.find().register(regexp, f)
        return decorated
