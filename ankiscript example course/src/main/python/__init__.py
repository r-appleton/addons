
import os.path
from .ankiscript import init_course

def about(course):
    from aqt.utils import showInfo
    showInfo('About ' + course.name)


init_course('Anki Script example course', 
    help=('html', 'index.html'), 
    setup='setup',
    lessons = [
        ('1: Verb infinitives', 'lesson1'),
        ('2: Present tense', 'lesson2'),
        ('3: Past tense', 'lesson3'),
        ('4: Verb aspects', 'lesson4')
    ],
    menu= 'Courses.Anki Script Example',
    menuItems=[
        ('About', about)
    ])
