# -*- coding: utf-8 -*-

RULES = {
    'unchanged':{'description':'leave unchanged', 'function':lambda w: w},
    'lower case':{'description':'convert to lower case', 'function':lambda w: w.lower()}, 
    'capitalize':{'description':'capitalize first word', 'function':lambda w: w.capitalize()}, 
    'replace \u0451 with \u0435':{'description':'(Russian) replace \u0451 with \u0435', 'function':lambda w: w.replace('\u0451', '\u0435')}
}
