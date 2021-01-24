
import os
import unittest
import tests.mockanki
from unittest.mock import patch
from ankiscript.course import Course

class CourseTest(unittest.TestCase):

    @patch('ankiscript.datasource.LocalDirectoryDataSource')
    @patch('ankiscript.course.Addin')
    def test_update(self, Addin, LocalDirectoryDataSource):
        LocalDirectoryDataSource.commands.return_value = ['# comment']
        Addin._module.return_value = 'testing'
        
        self._course = Course('testing', '123456')
        self._course._update(os.path.dirname(__file__))

    @patch('ankiscript.course.openLink')
    def test_help(self, openLink):
        course = Course('testing', 'zzz')
        course.help()
        openLink.assert_called_with('file:///' + os.path.join('zzz', 'index.html'))
        course.help('testing.html')
        openLink.assert_called_with('file:///' + os.path.join('zzz', 'testing.html'))
        
        course = Course('testing', ('abc','xyz.html'))
        course.help()
        openLink.assert_called_with('file:///' + os.path.join('abc', 'xyz.html'))
        course.help('testing.html')
        openLink.assert_called_with('file:///' + os.path.join('abc', 'testing.html'))

        