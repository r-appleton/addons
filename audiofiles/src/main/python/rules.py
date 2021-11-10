# -*- coding: utf-8 -*-

RULES = {
    'unchanged':{'description':'leave unchanged', 'function':lambda w: w},
    'lower case':{'description':'convert to lower case', 'function':lambda w: w.lower()}, 
    'capitalize':{'description':'capitalize first word', 'function':lambda w: w.capitalize()}, 
    'replace ё with е':{'description':'(Russian) replace ё with е', 'function':lambda w: w.replace('ё', 'е')}
}
