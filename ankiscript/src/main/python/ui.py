from aqt.qt import *
import aqt
from aqt.utils import openLink, GetTextDialog

TITLE = 'Anki'

class GetTextDialogEx(GetTextDialog):
    def __init__(self, parent, question, help=None, edit=None, default="", title=TITLE, minWidth=400):
         GetTextDialog.__init__(self, parent, question, help, edit, default, title, minWidth)
         
    def helpRequested(self):
        openLink(self.help)
    
# need to copy getText with custom dialog to avoid connecting to AnkiHelp site
def getText(prompt, parent=None, help=None, edit=None, default="", title=TITLE, geomKey=None, **kwargs):
    if not parent:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    d = GetTextDialogEx(parent, prompt, help=help, edit=edit, default=default, title=title, **kwargs)
    d.setWindowModality(Qt.WindowModal)
    if geomKey:
        restoreGeom(d, geomKey)
    ret = d.exec_()
    if geomKey and ret:
        saveGeom(d, geomKey)
    return (str(d.l.text()), ret)


# need to copy askUser to avoid connecting to AnkiHelp site
def askUser(text, parent=None, help="", defaultno=False, msgfunc=None, title=TITLE, **kwargs):
    "Show a yes/no question. Return true if yes."
    if not parent:
        parent = aqt.mw.app.activeWindow()
    if not msgfunc:
        msgfunc = QMessageBox.question
    sb = QMessageBox.Yes | QMessageBox.No
    if help:
        sb |= QMessageBox.Help
    while 1:
        if defaultno:
            default = QMessageBox.No
        else:
            default = QMessageBox.Yes
        r = msgfunc(parent, title, text, sb, default)
        if r == QMessageBox.Help:
            openLink(help)
        else:
            break
    return r == QMessageBox.Yes
