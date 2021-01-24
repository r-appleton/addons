
import unittest
from unittest.mock import patch, call, Mock
from ankiscript.modeldata import ModelData, Template
from ankiscript.datasource import LocalDirectoryDataSource
from ankiscript.execution import AdHocExecution

class ModelDataTest(unittest.TestCase):

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_set_note(self, read, createModel):
        read.return_value = 'css'
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.set_note(createModel, 'word', False)
            self.assertEqual(data._action, createModel)
            self.assertEqual(data._note, ('word', False, 'css'))
            self.assertEqual(data._templates, [])

    @patch('ankiscript.database.editModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_set_cloze_note(self, read, editModel):
        read.return_value = None
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.set_note(editModel, 'cloze', True)
            self.assertEqual(data._action, editModel)
            self.assertEqual(data._note, ('cloze', True, None))
            self.assertEqual(data._templates, [Template('cloze', None, None, None)])

    def test_add_parameter(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.add_parameter('ONE', ['a', 'b'])
            self.assertEqual(data._params, [('ONE', ['a', 'b'])])

            data.add_parameter('TWO', ['x and y'])
            self.assertEqual(data._params, [('ONE', ['a', 'b']), ('TWO', ['x and y'])])

    def test_add_field(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.add_fields(['Russian'])
            self.assertEqual(data._fields, ['Russian'])

            data.add_fields(['English'])
            self.assertEqual(data._fields, ['Russian', 'English'])

    def test_add_fields(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.add_fields(['Russian', 'English'])
            self.assertEqual(data._fields, ['Russian', 'English'])

    def test_duplicate_field_ignored(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.add_fields(['Russian', 'English'])
            data.add_fields(['English'])
            self.assertEqual(data._fields, ['Russian', 'English'])

    def test_add_parameterized_field(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            # unparameterized field should only be added once
            data.add_parameter('ONE', ['a', 'b'])
            data.add_fields(['Russian', 'Audio (${ONE})'])
            self.assertEqual(data._fields, ['Russian',  'Audio (a)',  'Audio (b)'])

    def test_add_parameterized_multiple_field(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            # unparameterized field should only be added once
            data.add_parameter('ONE', ['a', 'b'])
            data.add_fields(['Russian ($ONE)', 'Audio ($ONE)'])
            data.add_fields(['Russian'])
            self.assertEqual(data._fields, ['Russian (a)',  'Audio (a)', 'Russian (b)', 'Audio (b)', 'Russian'])

    def test_add_multi_parameterized_field(self):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            # unparameterized field should only be added once
            # parameterized field should have instances expanded
            # multi-parameterized field should have instances expanded, in order parameters were added (not in the field name)
            data.add_parameter('ONE', ['a', 'b'])
            data.add_parameter('TWO', ['x', 'y'])
            data.add_fields(['Field1'])
            data.add_fields(['Field2 (${ONE})'])
            data.add_fields(['Field3 (${TWO})'])
            data.add_fields(['Field4 (${TWO}, ${ONE})'])
            self.assertEqual(data._fields, ['Field1', 'Field2 (a)', 'Field2 (b)', 'Field3 (x)', 'Field3 (y)', 'Field4 (x, a)', 'Field4 (y, a)', 'Field4 (x, b)', 'Field4 (y, b)'])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_template(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            read.return_value = '<card text>'
            data.add_templates(['e>r'], 'vocabulary')
            self.assertEqual(data._templates, [Template('e>r', 'vocabulary', '<card text>', '<card text>')])

            data.add_templates(['r>e'])
            self.assertEqual(data._templates, [
                Template('e>r', 'vocabulary', '<card text>', '<card text>'), 
                Template('r>e', None, '<card text>', '<card text>')
                ])

    @patch('ankiscript.database.editModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_template_to_cloze_note(self, read, editModel):
        read.return_value = 'css'
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            data.set_note(editModel, 'cloze', True)
            with self.assertRaises(Exception, msg='cards cannot be added to a cloze note type'):
                data.add_templates(['e>r'], 'vocabulary')

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_templates(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            read.return_value = '<card text>'
            data.add_templates(['e>r', 'r>e'], 'vocabulary')
            self.assertEqual(data._templates, [
                Template('e>r', 'vocabulary', '<card text>', '<card text>'), 
                Template('r>e', 'vocabulary', '<card text>', '<card text>')
                ])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_parameterized_template(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            read.return_value = '{{Field (${ONE})}}'
            data.add_parameter('ONE', ['a', 'b'])
            data.add_templates(['e>r (${ONE})'], 'vocabulary')
            self.assertEqual(data._templates, [
                Template('e>r (a)', 'vocabulary', '{{Field (a)}}', '{{Field (a)}}'),
                Template('e>r (b)', 'vocabulary', '{{Field (b)}}', '{{Field (b)}}')
                ])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_parameterized_and_translated_template(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            read.return_value = '$${ONE} $${TWO}'
            data.add_parameter('ONE', ['a', 'b'])
            data.add_parameter('TWO', ['1', '2'])
            data.add_translation('ONE', ['x', 'y'])
            data.add_translation('TWO', ['i', 'ii'])
            data.add_templates(['e>r (${ONE}${TWO})'], 'vocabulary')
            self.assertEqual(data._templates, [
                Template('e>r (a1)', 'vocabulary', 'x i', 'x i'),
                Template('e>r (a2)', 'vocabulary', 'x ii', 'x ii'),
                Template('e>r (b1)', 'vocabulary', 'y i', 'y i'),
                Template('e>r (b2)', 'vocabulary', 'y ii', 'y ii')
                ])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_translation_with_no_parameter(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            with self.assertRaisesRegex(Exception, 'Parameter ONE is required before any translations for it'):
                data.add_translation('ONE', ['x', 'y'])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_translation_with_wrong_number_of_values(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            with self.assertRaisesRegex(Exception, 'Parameter ONE has 2 values, but 3 translations'):
                data.add_parameter('ONE', ['a', 'b'])
                data.add_translation('ONE', ['x', 'y', 'z'])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_add_multi_parameterized_template(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            read.return_value = '{{Field (${ONE},${TWO})}}'
            data.add_parameter('ONE', ['a', 'b'])
            data.add_parameter('TWO', ['x', 'y'])
            data.add_templates(['e>r (${ONE},${TWO})', 'r>e (${ONE},${TWO})'], None)
            self.assertEqual(data._templates, [
                Template('e>r (a,x)', None, '{{Field (a,x)}}', '{{Field (a,x)}}'),
                Template('r>e (a,x)', None, '{{Field (a,x)}}', '{{Field (a,x)}}'),
                Template('e>r (a,y)', None, '{{Field (a,y)}}', '{{Field (a,y)}}'),
                Template('r>e (a,y)', None, '{{Field (a,y)}}', '{{Field (a,y)}}'),
                Template('e>r (b,x)', None, '{{Field (b,x)}}', '{{Field (b,x)}}'),
                Template('r>e (b,x)', None, '{{Field (b,x)}}', '{{Field (b,x)}}'),
                Template('e>r (b,y)', None, '{{Field (b,y)}}', '{{Field (b,y)}}'),
                Template('r>e (b,y)', None, '{{Field (b,y)}}', '{{Field (b,y)}}')
                ])

    @patch('ankiscript.database.createModel')
    @patch('ankiscript.datasource.DataSource.read')
    def test_duplicate_template_ignored(self, read, createModel):
        with ModelData(AdHocExecution(), LocalDirectoryDataSource(None)) as data:
            read.return_value = 'css'
            data.set_note(createModel, 'word', False)
            read.return_value = None
            data.add_templates(['e>r', 'r>e'], 'vocabulary')
            data.add_templates(['e>r', 'r>e'], 'vocabulary')
            self.assertEqual(data._templates, [Template('e>r', 'vocabulary', None, None), Template('r>e', 'vocabulary', None, None)])
