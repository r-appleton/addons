
import re
import tempfile
from aqt.utils import showInfo
from .command import command
from .registery import CommandRegistery
from .modeldata import ModelData
from .menus import click_menu_item
from .addin import Addin
from .ui import askUser
from .database import createDeck, setDefaultDeck, createNote, setFields


# called by Parser to init syntax parsing
def init(parser):
    parser.add_syntax(lambda line, **kwargs: CommandRegistery.find().parse(line, **kwargs))


@command(r'^\s*')
def _whitespace(**kwargs):
    pass
    
@command(r'^\s*#.*')
def _comment(**kwargs):
    pass

@command(r'display message: {message}')
def _comment(message, **kwargs):
    showInfo(message, title=kwargs['course'].name)

@command(r'open {name} help page')
def _open_help(name, **kwargs):
    if hasattr(kwargs['course'], 'help'):
        name = _unquote(name)
        kwargs['course'].help('index.html' if name == 'main' else name)
    else:
        kwargs['parser'].add_warning('Ignored: open {0} help page'.format(name))

@command(r'click {name} menu item')
def _click_menu_item(name, **kwargs):
    click_menu_item(_unquote(name))

@command(r'set {alias} dir, asking {prompt}')
def _set_dir(alias, prompt, **kwargs):
    if not kwargs['course'].set_dir(_unquote(alias), tempfile.tempdir, _unquote(prompt)):
        raise Exception('A directory must be specified')

@command(r'set {name} alias, asking {prompt}, with default {default}')
def _set_alias(name, default, prompt, **kwargs):
    if not kwargs['course'].set_alias(_unquote(name), _unquote(default), _unquote(prompt)):
        raise Exception('A directory must be specified')
   
@command(r'set {name} flag, asking {prompt}, with default {default}')
def _set_flag(name, default, prompt, **kwargs):
    defaultno = default.lower() in ['false', 'no']
    kwargs['course'].set_flag(_unquote(name), defaultno, _unquote(prompt))

@command(r'install addin {id} ({name})')
def _install_addin(name, id, **kwargs):
    Addin(_unquote(name)).install(_unquote(id.strip()), kwargs['course'])

@command(r'configure {name} addin')
def _configure_addin(name, **kwargs):
    Addin(_unquote(name)).configure(kwargs['datasource'], kwargs['course'])

@command(r'configure {name} addin, setting key {key}')
def _configure_addin(name, key, **kwargs):
    Addin(_unquote(name)).configure(kwargs['datasource'], kwargs['course'], _split(key, sep='/'))

# TODO. if a key contains a comma this method fails
#       for now as a work around above syntax can be called multiple times
@command(r'configure {name} addin, setting keys {keys}')
def _configure_addin(name, keys, **kwargs):
    addin = Addin(_unquote(name))
    for key in _split(keys):
        addin.configure(kwargs['datasource'], kwargs['course'], _split(key, sep='/'))

@command('copy all files from {source} to {destination}')
def _copy_files(source, destination, **kwargs):
    if kwargs['course'].get_flag(_unquote(source), default=False):
        destination = kwargs['course'].get_alias(_unquote(destination))
        kwargs['datasource'].copy_files(_unquote(source), destination)

@command('copy files from {source} to {destination}, asking {prompt}')
def _copy_files_with_prompt(source, destination, prompt, **kwargs):
    if kwargs['course'].set_flag(_unquote(source), True, _unquote(prompt)):
        destination = kwargs['course'].get_alias(_unquote(destination))
        kwargs['datasource'].copy_files(_unquote(source), destination)

@command('copy {name} from {source} to {destination}')
def _copy_file(name, source, destination, **kwargs):
    if _unquote(destination) == 'Anki media collection':
        kwargs['datasource'].install_media_file(_unquote(name))
    else:
        if kwargs['course'].get_flag(_unquote(source), default=False):
            destination = kwargs['course'].get_alias(_unquote(destination))
            kwargs['datasource'].copy_file(_unquote(name), _unquote(source), destination)

@command(r'create decks {decks}')
def _add_decks(decks, **kwargs):
    for deck in _split_names(decks):
        _create_deck(deck, **kwargs)

@command(r'create deck {deck}')
def _add_deck(deck, **kwargs):
    _create_deck(_unquote(deck), **kwargs)

@command(r'set default deck to {deck} for {model} card type {template}')
def _set_default_deck(model, template, deck, **kwargs):
    deck = kwargs['course'].get_alias(_unquote(deck))
    notetype = kwargs['course'].get_alias(_unquote(model))
    if notetype and deck:
        setDefaultDeck(notetype, _unquote(template), deck)

@command(r'set default deck to {deck} for {model} card types {templates}')
def _set_default_deck(model, templates, deck, **kwargs):
    deck = kwargs['course'].get_alias(_unquote(deck))
    if deck:
        for template in _split_names(templates):
            notetype = kwargs['course'].get_alias(_unquote(model))
            if notetype:
                setDefaultDeck(notetype, template, deck)

@command(r'add {model} note, setting fields {fields}')
def _add_note_and_field_values(model, fields, **kwargs):
    deck = kwargs['course'].get_alias('default')
    notetype = kwargs['course'].get_alias(_unquote(model))
    if notetype and deck:
        fields = _split_key_value_pairs(fields)
        _ensure_media_files_installed(fields, **kwargs)
        createNote(deck, notetype, fields)
    
@command(r'for {model} {note} set fields {fields}')
def _set_field_values(model, fields, note, **kwargs):
    _set_field_values(_unquote(model), _unquote(note), _split_key_value_pairs(fields), **kwargs)

@command(r'for {model} {note} set field {field} to {value}')
def _set_field_value(model, note, field, value, **kwargs):
    _set_field_values(_unquote(model), _unquote(note), {_unquote(field):_unquote(value)}, **kwargs)

#... creating/changing note types

@command(r'create {model} note type and {commands}')
def _create_model(model, commands, **kwargs):
    _process_model_data(ModelData.create, model, False, commands, **kwargs)

@command(r'create {model} cloze type and {commands}')
def _create_cloze_model(model, commands, **kwargs):
    _process_model_data(ModelData.create, model, True, commands, **kwargs)

@command(r'change {model} note type and {commands}')
def _edit_model(model, commands, **kwargs):
    _process_model_data(ModelData.edit, model, None, commands, **kwargs)

#.... note type sub-commands

@command(r'with {parameters}')
def _with_parameters(parameters, **kwargs):
    #with ONE in [a, b, c], TWO in [d, e, "f and g"] and THREE in [x, y, z]:
    # note param order is preserved
    regexp = r'\s*(?P<quote1>[\'"]|\b)(?P<key>.*?)(?P=quote1)\s*in\s*\[(?P<value>.*?)\]\s*(?:,|and|$)'
    for m in re.finditer(regexp, parameters):
        kwargs['context'].add_parameter(m.group('key'), _split(m.group('value')))

@command(r'translate {name} to [{values}]')
def _add_translation(name, values, **kwargs):
    kwargs['context'].add_translation(_unquote(name), _split(values))

@command(r'add field {field}')
def _add_field_to_context(field, **kwargs):
    kwargs['context'].add_fields([field])

@command(r'add fields {fields}')
def _add_fields_to_context(fields, **kwargs):
    kwargs['context'].add_fields(_split_names(fields))

@command(r'add card type {template}, setting default deck to {deck}')
def _add_card_to_context(template, deck, **kwargs):
    kwargs['context'].add_templates([_unquote(template)], _unquote(deck))

@command(r'add card types {templates}, setting default deck to {deck}')
def _add_cards_to_context(templates, deck, **kwargs):
    kwargs['context'].add_templates(_split_names(templates), _unquote(deck))

@command(r'change card type {template}')
def _add_card_change_to_context(template, **kwargs):
    kwargs['context'].add_templates([_unquote(template)])

@command(r'change card types {templates}')
def _add_card_changes_to_context(templates, **kwargs):
    kwargs['context'].add_templates(_split_names(templates))

def _process_model_data(action, model, cloze, commands, **kwargs):
    with ModelData(kwargs['course'], kwargs['datasource']) as data:
        data.set_note(action, model, cloze)
        for cmd in commands.split(';'):
            kwargs['parser'].parse_line(cmd.strip(), context=data)

def _create_deck(deck, **kwargs):
    deck = kwargs['course'].get_alias(deck)
    if deck:
        try:
            createDeck(deck)
        except DuplicateException as x:
            # permit users to map multiple aliases to the same deck if they really want to
            if not askUser('Deck {0} already exists - continue?'.format(deck)):
                raise x

def _set_field_values(model, note, fields, **kwargs):
    notetype = kwargs['course'].get_alias(model)
    if notetype:
        _ensure_media_files_installed(fields, **kwargs)
        setFields(notetype, note, fields)

def _ensure_media_files_installed(fields, **kwargs):
    '''
    Checks if field values contain image (<img src="...">) or sound data ([sound:...]), 
    and if so installs media file(s)
    '''
    for name in fields.keys():
        _ensure_media_file_installed(fields, name, r'<img src="(?P<filename>.*?)">', **kwargs)
        _ensure_media_file_installed(fields, name, r'\[sound:(?P<filename>.*?)\]', **kwargs)

def _ensure_media_file_installed(fields, name, pattern, **kwargs):
    for m in re.finditer(pattern, fields[name]):
        filename = m.group('filename')
        installed = kwargs['datasource'].install_media_file(filename)
        if not installed:
            kwargs['parser'].add_warning('{0} media file was not installed'.format(filename))
        elif installed != filename:
            # Anki renames files if a media file already exists with this name so must use that in field value
            fields[name] = fields[name].replace(filename, installed)

def _unquote(s):
    return s[1:-1] if s[0] in '\'"' and s[0] == s[-1] else s

def _split(s, sep=','):
    return [_unquote(value) for value in re.split(sep + r'\s*', s)] if s else []

def _split_names(s):
    regexp = r'\s*(?P<quote2>[\'"]|\b)(?P<value>.*?)(?P=quote2)\s*(?:,|and|$)'
    return [m.group('value') for m in re.finditer(regexp, s) if m.group('value') != '']

def _split_key_value_pairs(s):
    # list: a to 'b,x,y' , c to d and e to 'f and g'
    regexp = r'\s*(?P<quote1>[\'"]|\b)(?P<key>.*?)(?P=quote1)\s*to\s*(?P<quote2>[\'"]|\b)(?P<value>.*?)(?P=quote2)\s*(?:,|and|$)'
    return {m.group('key'):m.group('value') for m in re.finditer(regexp, s)}
    