# -*- coding: utf-8 -*-

import os.path
import copy
from anki.hooks import addHook
from anki.utils import stripHTMLMedia
from aqt import mw
from aqt.utils import showWarning
from .datasource import Datasource
from .dlgconfig import DlgConfig

from aqt.qt import *

datasource = Datasource()

def get_config():
    config = mw.addonManager.getConfig(__name__)
    if 'profiles' not in config:
        config['profiles'] = {}
    if mw.pm.name not in config['profiles']:
        original = copy.deepcopy(config)
        del original['profiles']
        config['profiles'][mw.pm.name] = original
    return config

def getWordToLookup(editor):
    if datasource.use_text_selection and editor.web.hasSelection():
        return editor.web.selectedText()
    else:
        return editor.note.fields[editor.currentField]

def onGetSoundFile(editor):
    word = stripHTMLMedia(getWordToLookup(editor))
    datasource.setConfig(get_config()['profiles'][mw.pm.name])
    filename = datasource.lookup(word)
    if filename:
        if datasource.use_text_selection and editor.web.hasSelection():
            editor.web.triggerPageAction(QWebEnginePage.Unselect)
        editor.addMedia(filename)
    else:
        showWarning('{0}: no sound data found'.format(word, title='Sound Files'))

def addEditorButton(buttons, editor):
    editor._links['audio'] = onGetSoundFile
    icon = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'audio.png'
    return buttons + [editor._addButton(icon, 'audio', 'lookup audio file')]

def configure():
    config = get_config()
    if DlgConfig(config['profiles'][mw.pm.name]).exec():
        mw.addonManager.writeConfig(__name__, config)
        datasource.setConfig(config['profiles'][mw.pm.name])

addHook('setupEditorButtons', addEditorButton)
mw.addonManager.setConfigAction(__name__, configure)
