
from aqt import mw
from anki.consts import MODEL_CLOZE
from anki.notes import Note
from anki.utils import stripHTMLMedia


# Based on https://github.com/dae/anki/blob/master/anki/stdmodels.py
# to improve error handling:
# ... refer to https://github.com/FooSoft/anki-connect/blob/master/AnkiConnect.py (https://github.com/FooSoft/anki-connect)


class DuplicateException(Exception):
    def __init(self, msg):
        super(msg)


def createDeck(name):
    if name in mw.col.decks.allNames():
        raise DuplicateException('Deck "{0}" already exists'.format(name))
    mw.col.decks.id(name)

def setDefaultDeck(model, template, deck):
    m = _find_model(model)
    for t in m['tmpls']:
        if template == t['name']: 
            t['did'] = _find_deck(deck)
            mw.col.models.save(m)
            return
    raise Exception('Note type "{0}" does not have a card type "{1}"'.format(model, template))

def createModel(model, cloze, css, fields, templates):
    mm = mw.col.models
    if mm.byName(model):
        raise DuplicateException('Note type "{0}" already exists'.format(model))
    
    m = mm.new(model)
    if cloze:
        m['type'] = MODEL_CLOZE
    m['css'] = css

    # Anki must have at least 1 field and template in a new model
    for field in fields:
        mm.add_field(m, mm.new_field(field))

    for template in templates:
        t = mm.new_template(template.name)
        t['qfmt'] = template.front
        t['afmt'] = template.back
        if template.deck:
            t['did'] = _find_deck(template.deck)
        mm.add_template(m, t)

    mm.add(m)
    mm.save(m)

def editModel(model, css, fields, templates):
    mm = mw.col.models
    m = _find_model(model)

    # TODO check for incorrect model, deck, etc

    if css is not None:    
        m['css'] = css

    for field in fields:
        # need to check if new or an edit
        if field in m:
            raise DuplicateException('"{0}" field already exists for "{1}"'.format(field, model))
        else:
            mm.addField(m, mm.newField(field))

    for template in templates:
        # need to check if new or an edit
        t = _find_template(m, template.name)
        if t is None:
            t = mm.new_template(template.name)

        if template.front:
            t['qfmt'] = template.front
        if template.back:
            t['afmt'] = template.back
        if template.deck:
            t['did'] = _find_deck(template.deck)
        mm.add_template(m, t)

    mm.save(m)

def createNote(deck, model, fields):
    m = _find_model(model)
    m['did'] = _find_deck(deck)
    
    note = Note(mw.col, m)
    _set_fields(note, fields)
    mw.col.addNote(note)
    
    duplicateOrEmpty = note.dupeOrEmpty()
    if duplicateOrEmpty == 1:
        raise Exception('cannot create note because it is empty')
    elif duplicateOrEmpty == 2:
        key = m['flds'][0]['name']
        value = stripHTMLMedia(fields[key]) if key in fields else ''
        raise DuplicateException('"{0}" note already exists for "{1}"'.format(model, value))
    elif duplicateOrEmpty == False:
        return
    else:
        raise Exception('cannot create note for unknown reason')

def setFields(model, note, fields):
    m = _find_model(model)
    
    for id in mw.col.findNotes(note):
        n = mw.col.getNote(id)
        if n.mid == m['id']:
            _set_fields(n, fields)
            n.flush()
            return
    raise Exception('Cannot find "{0}" "{1}" note'.format(model, note))
    
def _find_deck(deck):
    d = mw.col.decks.byName(deck)
    if not d:
        raise Exception('Deck "{0}" does not exist'.format(deck))
    return d['id']
    
def _find_model(model):
    m = mw.col.models.byName(model)
    if not m:
        raise Exception('Note type "{0}" does not exist'.format(model))
    return m

def _set_fields(note, fields):
    for (field, value) in fields.items():
        if field == 'Tags':
            note.addTag(value)
        else:
            note[field] = value

def _find_template(note, name):
    for t in note['tmpls']:
        if t['name'] == name:
            return t
    return None
