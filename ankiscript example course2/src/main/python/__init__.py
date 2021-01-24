
import os.path
from .ankiscript import init_course
from .syntax import init


init_course('Anki Script example course with custom syntax', 
    help=('html', 'index.html'), 
    setup='setup',
    lessons = [
        ('1: Verb infinitives', 'lesson1'),
        ('2: Present tense', 'lesson2'),
        ('3: Past tense', 'lesson3'),
        ('4: Verb aspects', 'lesson4')
    ],
    menu= 'Courses.Anki Script example custom syntax',
    syntax = init
    )
