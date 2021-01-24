
from aqt import mw
from aqt.qt import QAction


def find_menu(name, parent, create=False):
    for action in parent.actions():
        if action.text().replace('&','') == name:
            return action.menu()
    if create:
        return parent.addMenu(name)

    raise Exception('Menu {0} was not found'.format(name))


def add_menu_item(key, callback):
    dialog = key.endswith('...')
    names = key[:-3].split('.') if dialog else key.split('.')
    mnu = mw.form.menubar
    
    for name in names[:-1]:
        mnu = find_menu(name, mnu, True)
        
    if callback is None:
        mnu = find_menu(names[-1], mnu, True)
        if len(mnu.actions()):
            mnu.addSeparator()
    else:
        text = names[-1] + '...' if dialog else names[-1]
        # check menu item does not already exist
        for action in mnu.actions():
            if action.text().replace('&','') == text:
                return
        return mnu.addAction(text, callback)



def click_menu_item(key):
    dialog = key.endswith('...')
    names = key[:-3].split('.') if dialog else key.split('.')
    mnu = mw.form.menubar
    
    for name in names[:-1]:
        mnu = find_menu(name, mnu)

    text = names[-1] + '...' if dialog else names[-1]
    for action in mnu.actions():
        if action.text().replace('&','') == text:
            action.activate(QAction.Trigger)
