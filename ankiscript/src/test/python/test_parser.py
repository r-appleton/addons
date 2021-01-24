
import os
import unittest
from unittest.mock import patch, call, Mock
from ankiscript.parser import Parser
from ankiscript.datasource import DataSource

class ParserTest(unittest.TestCase):

    @patch('ankiscript.datasource.DataSource.read')
    def test_parse_empty_line(self, read):
        read.return_value = ''
        with Parser(None, DataSource()) as parser:
            self.assertEqual(parser._commands, [''])

    @patch('ankiscript.datasource.DataSource.read')
    def test_parse_single_line_command(self, read):
        read.return_value = 'fred was here'
        with Parser(None, DataSource()) as parser:
            self.assertEqual(parser._commands, ['fred was here'])

    @patch('ankiscript.datasource.DataSource.read')
    def test_parse_multiline_command_using_comma(self, read):
        read.return_value = '''for verbs set fields A=fred, 
                                   B=bill'''
        with Parser(None, DataSource()) as parser:
            self.assertEqual(parser._commands, ['for verbs set fields A=fred, B=bill'])

    @patch('ankiscript.datasource.DataSource.read')
    def test_parse_multiline_command_using_colon(self, read):
        read.return_value = '''for verbs set fields:
                                   A=fred, B=bill'''
        with Parser(None, DataSource()) as parser:
            self.assertEqual(parser._commands, ['for verbs set fields A=fred, B=bill'])

    @patch('ankiscript.datasource.DataSource.read')
    def test_parse_multiline_notetype_command(self, read):
        read.return_value = '''create verb note type and:
                                   add fields Russian, Audio, English;
                                   add card types e>r, r>e, setting default deck to verbs'''
        with Parser(None, DataSource()) as parser:
            self.assertEqual(parser._commands, ['create verb note type and add fields Russian, Audio, English; add card types e>r, r>e, setting default deck to verbs'])
