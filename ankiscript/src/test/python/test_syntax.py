
import os
import unittest
from unittest.mock import patch, call, Mock, MagicMock
from ankiscript.course import Course
from ankiscript.datasource import DataSource
from ankiscript.parser import Parser
from ankiscript.modeldata import ModelData
from ankiscript.syntax import _unquote, _split, _split_key_value_pairs, init

course = Course('testing')
datasource = DataSource()
datasource._read = Mock()


class SyntaxTest(unittest.TestCase):
    def test_unquote(self):
        self.assertEqual(_unquote('abc'), 'abc')
        self.assertEqual(_unquote('"abc"'), 'abc')
        self.assertEqual(_unquote("'abc'"), 'abc')
        self.assertEqual(_unquote('"abc'), '"abc')
        self.assertEqual(_unquote("'abc"), "'abc")
        self.assertEqual(_unquote('abc"'), 'abc"')
        self.assertEqual(_unquote("abc'"), "abc'")

    def test_split(self):
        self.assertEqual(_split(''), [])
        self.assertEqual(_split('a'), ['a'])
        self.assertEqual(_split('"a"'), ['a'])
        self.assertEqual(_split('a,b'), ['a','b'])
        self.assertEqual(_split('a,"b"'), ['a','b'])
        self.assertEqual(_split('"a",b'), ['a','b'])
        self.assertEqual(_split('"a","b"'), ['a','b'])
        self.assertEqual(_split('a,b, c'), ['a','b','c'])
        self.assertEqual(_split('a:b', sep=':'), ['a','b'])

    def test_split_key_value_pairs(self):
        self.assertEqual(_split_key_value_pairs(''), {})
        self.assertEqual(_split_key_value_pairs('a to 1'), {'a':'1'})
        self.assertEqual(_split_key_value_pairs('"a" to 1'), {'a':'1'})
        self.assertEqual(_split_key_value_pairs('a to 1, b to 2'), {'a':'1', 'b':'2'})
        self.assertEqual(_split_key_value_pairs('a to 1 and b to 2'), {'a':'1', 'b':'2'})
        self.assertEqual(_split_key_value_pairs('a to 1, b to "2 and 3"'), {'a':'1', 'b':'2 and 3'})
        self.assertEqual(_split_key_value_pairs('a to 1 and b to "2 and 3"'), {'a':'1', 'b':'2 and 3'})
        self.assertEqual(_split_key_value_pairs("a to 1 and b to 'x,y,z' and c to 2"), {'a':'1', 'b':'x,y,z', 'c':'2'})

    def test_parse_whitespace(self):
        self._parse(' ')

    def test_parse_comment(self):
        self._parse('# a comment')

    @patch('ankiscript.course.Course.help')
    def test_parse_open_help_page(self, help):
        self._parse('open main help page')
        help.assert_called_with('index.html')

        self._parse('open "layouts.html" help page')
        help.assert_called_with('layouts.html')

    @patch('ankiscript.syntax.click_menu_item')
    def test_parse_click_menu_item(self, click_menu_item):
        self._parse('click "Aspect Pairs" menu item')
        click_menu_item.assert_called_with('Aspect Pairs')

    @patch('ankiscript.configurable.Configurable.set_dir')
    def test_parse_set_dir(self, set_dir):
        self._parse('set "the testing" dir, asking "What dir"')
        set_dir.assert_called_with('the testing', None, 'What dir')

    @patch('ankiscript.configurable.Configurable.set_alias')
    def test_parse_set_alias(self, set_alias):
        self._parse('set testing alias, asking "What value", with default "unknown"')
        set_alias.assert_called_with('testing', 'unknown', 'What value')

    @patch('ankiscript.configurable.Configurable.set_flag')
    def test_parse_set_flag(self, set_flag):
        self._parse('set testing flag, asking "What value", with default false')
        set_flag.assert_called_with('testing', True, 'What value')
        
        self._parse('set testing flag, asking "What value", with default true')
        set_flag.assert_called_with('testing', False, 'What value')

    @patch('ankiscript.addin.Addin.install')
    def test_parse_install_addin(self, install):
        self._parse('install addin 198750399 (Cloze Generator)')
        #Addin('Cloze Generator')
        install.assert_called_with('198750399', course)
        self._parse('install addin 498789867  (Replay buttons on card)')
        #self.assertEqual('Replay buttons on card')
        install.assert_called_with('498789867', course)

    @patch('ankiscript.addin.Addin.configure')
    def test_parse_configure_addin(self, configure):
        self._parse('configure "Cloze Generator" addin')
        #self.assertEqual(Addin._module, 'Cloze Generator')
        configure.assert_called_with(datasource, course)

    @patch('ankiscript.addin.Addin.configure')
    def test_parse_configure_addin_key(self, configure):
        self._parse('configure "Cloze Generator" addin, setting key a')
        #self.assertEqual(Addin._module, 'Cloze Generator')
        configure.assert_called_with(datasource, course, ['a'])

        self._parse('configure "Cloze Generator" addin, setting key a/b/c')
        #self.assertEqual(Addin._module, 'Cloze Generator')
        configure.assert_called_with(datasource, course, ['a','b','c'])

    @patch('ankiscript.addin.Addin.configure')
    @patch('ankiscript.course.Addin')
    def test_parse_configure_addin_keys(self, Addin, configure):
        self._parse('configure "Cloze Generator" addin, setting keys a, b')
        #self.assertEqual(Addin._module, 'Cloze Generator')
        configure.assert_has_calls([
            call(datasource, course, ['a']),
            call(datasource, course, ['b'])
            ])

        self._parse('configure "Cloze Generator" addin, setting keys "a/b/c", x/y/z')
        #self.assertEqual(Addin._module, 'Cloze Generator')
        configure.assert_has_calls([
            call(datasource, course, ['a','b','c']),
            call(datasource, course, ['x','y','z'])
            ])

    @patch('ankiscript.datasource.DataSource.copy_files')
    @patch('ankiscript.configurable.Configurable.get_alias')
    @patch('ankiscript.configurable.Configurable.get_flag')
    def test_parse_copy_files(self, get_flag, get_alias, copy_files):
        get_flag.return_value = True
        get_alias.side_effect = {'b':'zzz'}.get
        self._parse('copy all files from a to b')
        copy_files.assert_called_with('a', 'zzz')

    @patch('ankiscript.datasource.DataSource.copy_files')
    @patch('ankiscript.configurable.Configurable.get_alias')
    @patch('ankiscript.configurable.Configurable.get_flag')
    def test_parse_copy_files_when_flag_not_set(self, get_flag, get_alias, copy_files):
        get_flag.return_value = False
        get_alias.side_effect = {'b':'zzz'}.get
        self._parse('copy all files from a to b')
        copy_files.assert_not_called()

    @patch('ankiscript.datasource.DataSource.copy_files')
    @patch('ankiscript.configurable.Configurable.get_alias')
    @patch('ankiscript.configurable.Configurable.set_flag')
    def test_parse_copy_files_with_accepted_prompt(self, set_flag, get_alias, copy_files):
        set_flag.return_value = True
        get_alias.side_effect = {'b':'zzz'}.get
        self._parse('copy files from a to b, asking "do it?"')
        set_flag.assert_called_with('a', True, 'do it?')
        copy_files.assert_called_with('a', 'zzz')

    @patch('ankiscript.datasource.DataSource.copy_files')
    @patch('ankiscript.configurable.Configurable.get_alias')
    @patch('ankiscript.configurable.Configurable.set_flag')
    def test_parse_copy_files_with_rejected_prompt(self, set_flag, get_alias, copy_files):
        set_flag.return_value = False
        get_alias.side_effect = {'b':'zzz'}.get
        self._parse('copy files from a to b, asking "do it?"')
        set_flag.assert_called_with('a', True, 'do it?')
        copy_files.assert_not_called()
        
    @patch('ankiscript.datasource.DataSource.copy_file')
    @patch('ankiscript.configurable.Configurable.get_alias')
    @patch('ankiscript.configurable.Configurable.get_flag')
    def test_parse_copy_file(self, get_flag, get_alias, copy_file):
        get_flag.return_value = True
        get_alias.side_effect = {'b':'zzz'}.get
        self._parse('copy css from a to b')
        copy_file.assert_called_with('css', 'a', 'zzz')

    @patch('ankiscript.datasource.DataSource.install_media_file')
    def test_parse_copy_media_file(self, install_media_file):
        self._parse('copy image.jpg from media to Anki media collection')
        datasource.install_media_file.assert_called_with('image.jpg')

    @patch('ankiscript.syntax.createDeck')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_decks(self, get_alias, createDeck):
        get_alias.side_effect = {'vocabulary':'vocabulary', 'verb':'verb conjugation', 'grammar':'grammar', 'audio':'audio'}.get
        self._parse('create decks vocabulary, "verb", grammar, audio')
        createDeck.assert_has_calls([
            call('vocabulary'),
            call('verb conjugation'),
            call('grammar'),
            call('audio')
            ])

    @patch('ankiscript.syntax.createDeck')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_deck(self, get_alias, createDeck):
        get_alias.side_effect = {'verb':'verb conjugation'}.get
        self._parse('create deck "verb"')
        createDeck.assert_called_with('verb conjugation')

    @patch('ankiscript.syntax.setDefaultDeck')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_set_default_deck(self, get_alias, setDefaultDeck):
        get_alias.side_effect = {'vocabulary':'test vocabulary', 'pronoun':'test pronoun'}.get
        self._parse('set default deck to vocabulary for pronoun card type e>r (nom, m)')
        setDefaultDeck.assert_called_with('test pronoun', 'e>r (nom, m)', 'test vocabulary')

        self._parse('set default deck to vocabulary for pronoun card types "e>r (nom, m)", "r>e (nom, m)"')
        setDefaultDeck.assert_has_calls([
            call('test pronoun', 'e>r (nom, m)', 'test vocabulary'),
            call('test pronoun', 'r>e (nom, m)', 'test vocabulary')
            ])

    @patch('ankiscript.syntax.createNote')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_note_and_field_values(self, get_alias, createNote):
        get_alias.side_effect = {'default':'default', 'test word':'gendered word'}.get
        self._parse('add "test word" note, setting fields English to "hello world!" , "English (alt)" to fred')
        createNote.assert_called_with('default', 'gendered word', {'English':'hello world!', 'English (alt)':'fred'})

    @patch('ankiscript.syntax.setFields')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_set_field_values(self, get_alias, setFields):
        get_alias.side_effect = {'default':'default', 'test word':'gendered word'}.get
        self._parse('for "test word" hello set fields English to "hello world!", "English (alt)" to fred')
        setFields.assert_called_with('gendered word', 'hello', {'English':'hello world!', 'English (alt)':'fred'})

    @patch('ankiscript.syntax.setFields')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_set_field_value(self, get_alias, setFields):
        get_alias.return_value = 'test word'
        self._parse('for "test word" hello set field English to "hello world!"')
        setFields.assert_called_with('test word', 'hello', {'English':'hello world!'})

    @patch('ankiscript.syntax.setFields')
    @patch('ankiscript.datasource.DataSource.install_media_file')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_set_sound_field_value(self, get_alias, install_media_file, setFields):
        get_alias.return_value = 'test word'
        install_media_file.return_value = 'testing123.mp3'
        self._parse('for "test word" hello set field Audio to [sound:testing.mp3]')
        setFields.assert_called_with('test word', 'hello', {'Audio':'[sound:testing123.mp3]'})

    @patch('ankiscript.syntax.setFields')
    @patch('ankiscript.datasource.DataSource.install_media_file')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_set_image_field_value(self, get_alias, install_media_file, setFields):
        get_alias.return_value = 'test word'
        install_media_file.return_value = 'testing.jpg'
        self._parse('for "test word" hello set field Image to <img src="testing.jpg">')
        setFields.assert_called_with('test word', 'hello', {'Image':'<img src="testing.jpg">'})

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.set_note')
    def test_parse_create_note_type(self, set_note, create):
        self._parse('create gendered note type and ')
        set_note.assert_called_with(create, 'gendered', False)

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.set_note')
    def test_parse_create_cloze_type(self, set_note, create):
        self._parse('create gendered cloze type and ')
        set_note.assert_called_with(create, 'gendered', True)

    @patch('ankiscript.modeldata.ModelData.set_note')
    def test_parse_edit_model(self, set_note):
        self._parse('change gendered note type and with ')
        set_note.assert_called_with(ModelData.edit, 'gendered', None)

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_parameter')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_parameterized_commands(self, get_alias, add_parameter, create):
        get_alias.side_effect = {'Z':'Z'}.get
        data = [
            ['ONE in [a]', [('ONE', ['a'])]],
            ['ONE in [a,b]', [('ONE', ['a','b'])]],
            ['ONE in ["a",b]', [('ONE', ['a','b'])]],
            ['ONE in [a,"b"]', [('ONE', ['a','b'])]],
            ['ONE in ["a","b"]', [('ONE', ['a','b'])]],
            ["ONE in ['a','b']", [('ONE', ['a','b'])]],
            ['ONE in [a, b]', [('ONE', ['a','b'])]],
            ['ONE in [a,b], TWO in [x,y]', [('ONE', ['a','b']), ('TWO', ['x','y'])]],
            ['ONE in [a,b] and TWO in [x,y]', [('ONE', ['a','b']), ('TWO', ['x','y'])]],
            ['ONE in [a], TWO in ["x and y"] and THREE in [z]', [('ONE', ['a']), ('TWO', ['x and y']), ('THREE', ['z'])]],
            ['', []]
            ]
        for (cmd, params) in data:
            with self.subTest(msg=cmd):
                add_parameter.reset_mock()
                self._parse('create Z note type and with ' + cmd)
                if len(params):
                    assert add_parameter.call_count == len(params)
                    for (name, values) in params:
                        add_parameter.assert_any_call(name, values)
                else:
                    add_parameter.assert_not_called()

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_translation')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_translation(self, get_alias, add_translation, create):
        get_alias.side_effect = {'Z':'Z'}.get
        self._parse('create Z note type and translate ONE to ["x and y", z]')
        add_translation.assert_called_with('ONE', ['x and y', 'z'])

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_fields')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_field(self, get_alias, add_fields, create):
        get_alias.side_effect = {'Z':'Z'}.get
        self._parse('create Z note type and add field Word(past, ${GENDER})')
        add_fields.assert_called_with(['Word(past, ${GENDER})'])

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_fields')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_fields(self, get_alias, add_fields, create):
        get_alias.side_effect = {'Z':'Z'}.get
        self._parse('create Z note type and add fields "Word(past, ${GENDER})", Audio')
        add_fields.assert_called_with(['Word(past, ${GENDER})', 'Audio'])

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_card_type(self, get_alias, add_templates, create):
        get_alias.side_effect = {'Z':'Z', 'grammar':'grammar'}.get
        self._parse('create Z note type and add card type e>r (${GENDER}), setting default deck to grammar')
        add_templates.assert_called_with(['e>r (${GENDER})'], 'grammar')

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_card_type_quoted(self, get_alias, add_templates, create):
        get_alias.side_effect = {'Z':'Z', 'grammar':'grammar'}.get
        self._parse('create Z note type and add card types "${PERSON}", setting default deck to grammar')
        add_templates.assert_called_with(['${PERSON}'], 'grammar')

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_card_types(self, get_alias, add_templates, create):
        get_alias.side_effect = {'Z':'Z', 'grammar':'grammar'}.get
        self._parse('create Z note type and add card types e>r (${GENDER}), r>e (${GENDER}), setting default deck to grammar')
        add_templates.assert_called_with(['e>r (${GENDER})', 'r>e (${GENDER})'], 'grammar')

    @patch('ankiscript.modeldata.ModelData.edit')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_change_card_type(self, get_alias, add_templates, edit):
        get_alias.side_effect = {'Z':'Z', 'grammar':'grammar'}.get
        self._parse('change Z note type and change card type e>r (${GENDER})')
        add_templates.assert_called_with(['e>r (${GENDER})'])

    @patch('ankiscript.modeldata.ModelData.edit')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_change_card_types(self, get_alias, add_templates, edit):
        get_alias.side_effect = {'Z':'Z', 'grammar':'grammar'}.get
        self._parse('change Z note type and change card types e>r (${GENDER}), r>e (${GENDER})')
        add_templates.assert_called_with(['e>r (${GENDER})', 'r>e (${GENDER})'])

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.modeldata.ModelData.add_fields')
    @patch('ankiscript.modeldata.ModelData.set_note')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_add_fields_and_templates(self, get_alias, set_note, add_fields, add_templates, create):
        get_alias.side_effect = {'Z':'Z', 'grammar':'grammar'}.get
        cmd = 'create Z note type and add fields "Word(past, ${GENDER})", Audio; add card types e>r (${GENDER}), r>e (${GENDER}), setting default deck to grammar'
        self._parse(cmd)
        set_note.assert_called_with(create, 'Z', False)
        add_fields.assert_called_with(['Word(past, ${GENDER})', 'Audio'])
        add_templates.assert_called_with(['e>r (${GENDER})', 'r>e (${GENDER})'], 'grammar')

    @patch('ankiscript.modeldata.ModelData.create')
    @patch('ankiscript.modeldata.ModelData.add_templates')
    @patch('ankiscript.modeldata.ModelData.add_fields')
    @patch('ankiscript.modeldata.ModelData.set_note')
    @patch('ankiscript.configurable.Configurable.get_alias')
    def test_parse_multiline_command(self, get_alias, set_note, add_fields, add_templates, create):
        cmd = '''create ZZZ note type and:
                     add fields "one", two; 
                     add card types e>r, r>e, setting default deck to grammar'''

        datasource._read.return_value = cmd
        get_alias.side_effect = {'ZZZ':'ZZZ', 'grammar':'grammar'}.get

        with Parser(course, datasource) as parser:
            for cmd in parser:
                parser._parse(cmd, course=course, datasource=datasource)

        set_note.assert_called_with(create, 'ZZZ', False)
        add_fields.assert_called_with(['one', 'two'])
        add_templates.assert_called_with(['e>r', 'r>e'], 'grammar')

    def _parse(self, cmd):
        parser = Parser(course, datasource)
        parser._parse(cmd, course=course, datasource=datasource)

