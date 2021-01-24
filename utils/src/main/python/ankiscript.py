
"""
Utility functions to link an addin to Anki Script

This should be distributed in the addin package.
"""

import os.path
from aqt import mw, addons
from anki.httpclient import HttpClient
from typing import Optional
from types import ModuleType
from importlib import import_module


def init_course(name, help=None, setup=None, lessons=None, menu=None, menuItems=None, syntax=None):
    """Register a course with Anki Script.
    
    Keyword arguments:
    name      -- course name
    help      -- URL / directory with course help, optional (or tuple of URL / directory + main helkp page name)
    setup     -- package to initialize course, only required if the course requires initialization
    lessons   -- list of name, URL /directories, only required if the course has separate lessons 
    menu      -- menu to use for course actions, defaults to course name.
    menuItems -- additional menu items as a list of name, callback pairs, optional.
    syntax    -- function called with a single Parser arg to set up parsing using a different syntax from default one
               
    A 'package' is either pathname of a directory or zip file containing a command script and 
    associated data, or a callback function (taking the course object as the only parameter).  When 
    used for setting up a course the callback function should return True if the course setup was 
    successful.
    
    The command script can be saved using UTF-8 if it contains non Latin characters.
    
    The course actions can be added to a submenu by using a dot '.' in the menu name to specify the 
    menu hierarchy.
    
    No menu is added for the course if there are no actions for it (ie. it has no lessons and 
    custom actions).
    
    For additional menu items the callbacks must take the course object as the only parameter.  
    These are added as additional menu items at the end of the course menu, and enable custom 
    actions to be added for a course.  Providing a single value of None instead of a pair will 
    add a menu separator.

    The Course object is returned for use in the calling code, eg. for performing any custom 
    initialization.
    """
    if help:
        if isinstance(help, str):
            help = package(help)
        else:
            (d, page) = help
            help = (package(d), page)
    if setup:
        setup = package(setup)
    if lessons:
        lessons = [(name, package(d)) for (name, d) in lessons]

    ankiscript = importAnkiScript(True)
    return ankiscript.add_course(name, help=help, setup=setup, lessons=lessons, menu=menu, menuItems=menuItems, syntax=syntax)


def package(name):
    """If exists get pathname for a directory containing a command script and associated data distributed as part of the calling addon"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    if os.path.isdir(path):
        return path
    if os.path.isfile(path) and name.endswith('.zip'):
        return path
    # not a valid local file or directory, so assume that it points to a URL
    return name


def importAnkiScript(download=False):
    """private function to get a reference to the Anki Script addon, installing it if required"""

    if ankiscript := find_addon_by_name('Anki Script'):
        return ankiscript

    if download:
        id = '828860704'
        (id, result) = addons.download_and_install_addon(mw.addonManager, HttpClient(), id)
        if isinstance(result, addons.DownloadError):
            raise Exception('Anki Script download failed: {0}'.format(result))

        # now can try again to import
        return importAnkiScript(download=False)

    raise Exception('Cannot find Anki Script addin')


# https://forums.ankiweb.net/t/accessing-the-module-of-another-add-on/5936/2
def find_addon_by_name(addon_name: str) -> Optional[ModuleType]:
    for name in mw.addonManager.allAddons():
        if mw.addonManager.addonName(name) == addon_name:
            try:
                return import_module(name)
            except:
                pass
    return None
