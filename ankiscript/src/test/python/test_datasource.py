
import unittest
from ankiscript.datasource import _sanitise


class DatasourceTest(unittest.TestCase):
    def test_sanitise(self):
        self.assertEqual(_sanitise('a b'), 'a_b')
        self.assertEqual(_sanitise('a<b'), 'a_from_b')
        self.assertEqual(_sanitise('a>b'), 'a_to_b')
        self.assertEqual(_sanitise('a(b'), 'a_b')
        self.assertEqual(_sanitise('a)b'), 'a_b')
        self.assertEqual(_sanitise('a[b'), 'a_b')
        self.assertEqual(_sanitise('a]b'), 'a_b')
        self.assertEqual( _sanitise('a{b'), 'a_b')
        self.assertEqual(_sanitise('a}b'), 'a_b')
        self.assertEqual(_sanitise('a:b'), 'a_b')
        self.assertEqual(_sanitise('a$b'), 'ab')
        self.assertEqual(_sanitise('*ab'), 'ab')
        self.assertEqual(_sanitise('a${}b'), 'a_b')
        self.assertEqual(_sanitise('ab:'), 'ab')
        self.assertEqual(_sanitise('a${GENDER}b'), 'a_GENDER_b')
        self.assertEqual(_sanitise('a ${CASE} ${GENDER}'), 'a_CASE_GENDER')
        self.assertEqual(_sanitise('${PERSON}'), 'PERSON')
        self.assertEqual(_sanitise('${PERSON}.front'), 'PERSON.front')
        self.assertEqual(_sanitise('${PERSON}.back'), 'PERSON.back')
        self.assertEqual(_sanitise('e>r (past, ${GENDER}).front'), 'e_to_r_past_GENDER.front')
