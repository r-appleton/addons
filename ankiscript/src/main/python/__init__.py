
import os.path
from aqt.qt import QFileDialog
from aqt.utils import showInfo, openLink
from .course import Course
from .parser import Parser
from .menus import add_menu_item
from .ui import getText
from .execution import AdHocExecution


def add_course(name, help=None, setup=None, lessons=None, menu=None, menuItems=None, syntax=None):
    if not menu:
        menu = name
    course = Course(name, help, nosetup=setup == None, syntax=syntax)

    if setup and not course.get_flag('setup', default=False):
        # auto-setup fails as mw not initialized
        add_menu_item(menu + '.' + 'Setup', lambda: course.setup(setup))
    
    if isinstance(lessons, list):
        add_menu_item(menu, None)
        for (text, lesson) in lessons:
            add_menu_item(menu + '.' + text, onCourseUpdate(course, lesson, text))

    if isinstance(menuItems, list) and len(menuItems):
        add_menu_item(menu, None)
        for pair in menuItems:
            if pair is None:
                add_menu_item(menu, None)
            else:
                add_menu_item(menu + '.' + pair[0], lambda: pair[1](course))

    if help:
        add_menu_item(menu, None)
        add_menu_item(menu + '.' + 'Help...', course.help)
        
    return course

def onCourseUpdate(course, lesson, name):
    return lambda: course.upload(lesson, name)

def select_adhoc_script():
    dlg = QFileDialog()
    dlg.setAcceptMode(QFileDialog.AcceptOpen)
    dlg.setFileMode(QFileDialog.Directory)
    if dlg.exec():
        Parser.parse(dlg.selectedFiles()[0], AdHocExecution())


if __name__ == 'ankiscript':
    page = 'file:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manual', 'index.html')
    # try / except used to avoid unit test issues
    try:
        add_menu_item('Tools.Anki Script.Run script...', lambda: select_adhoc_script())
#        add_menu_item('Tools.Anki Script.Create script...', lambda: openLink(page))
        add_menu_item('Tools.Anki Script', None)
        add_menu_item('Tools.Anki Script.Manual...', lambda: openLink(page))
    except:
        pass
