# -*- coding: utf-8 -*-

import os.path
from anki.hooks import addHook
from anki.utils import stripHTMLMedia
from aqt import mw
from aqt.utils import showWarning
from .datasource import Datasource
from .dlgconfig import DlgConfig

from aqt.qt import *

datasource = Datasource()
datasource.setConfig(mw.addonManager.getConfig(__name__))

def getWordToLookup(editor):
    if datasource.use_text_selection and editor.web.hasSelection():
        return editor.web.selectedText()
    else:
        return editor.note.fields[editor.currentField]

def onGetSoundFile(editor):
    word = stripHTMLMedia(getWordToLookup(editor))
    filename = datasource.lookup(word.lower())
    if filename:
        editor.addMedia(filename)
    else:
        showWarning('{0}: no sound data found'.format(word, title='Sound Files'))

def addEditorButton(buttons, editor):
    editor._links['audio'] = onGetSoundFile
    icon = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'audio.png'
    return buttons + [editor._addButton(icon, 'audio', 'lookup audio file')]

def configure():
    config = mw.addonManager.getConfig(__name__)
    if DlgConfig(config).exec():
        mw.addonManager.writeConfig(__name__, config)
        datasource.setConfig(mw.addonManager.getConfig(__name__))

addHook('setupEditorButtons', addEditorButton)
mw.addonManager.setConfigAction(__name__, configure)
