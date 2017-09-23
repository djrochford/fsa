import unittest
from cfg import CFG

class TestCFG(unittest.TestCase):

    def setUp(self):
        self.rules1 = {
            'A': {'0A1', 'B'},
            'B': {'#'}
        }

        rules2 = {
            '<SENTENCE>': {'<NOUN-PHRASE> <VERB-PHRASE>'},
            '<NOUN-PHRASE>': {'<CMPLX-NOUN>', '<CMPLX-NOUN> <PREP-PHRASE>'},
            '<VERB-PHRASE>': {'<CMPLX-VERB>', '<CMPLX-VERB> <PREP-PHRASE>'},
            '<PREP-PHRASE>': {'<PREP> <CMPLX-NOUN>'},
            '<CMPLX-NOUN>': {'<ARTICLE> <NOUN>'},
            '<CMPLX-VERB>': {'<VERB>', '<VERB> <NOUN-PHRASE>'},
            '<ARTICLE>': {'a'},
            '<ARTICLE>': {'the'},
            '<NOUN>': {'boy', 'girl', 'flower'},
            '<VERB>': {'touches', 'likes', 'sees'},
            '<PREP>': {'with'}
        }

        rules3 = {
            'S': {'aSb','SS', '€'}
        }

        rules4 = {
            '<EXPR>': {'<EXPR>+<TERM>', '<TERM>'},
            '<TERM>': {'<TERM>*<FACTOR>', '<FACTOR>'},
            '<FACTOR>': {'(<EXPR>)', 'a'}
        }

        self.g1 = CFG(self.rules1, 'A')
        self.g2 = CFG(rules2, '<SENTENCE>')
        self.g3 = CFG(rules3, 'S')
        self.g4 = CFG(rules4, '<EXPR>')

    def test_instantiation(self):
        not_dict_msg = "Rules parameter should be a dictionary."
        bad_variables_msg = "Variable '0' is not a string."
        bad_values_msg = "Values ('#', '01'|'01', '#') of rules dictionary are not either sets or frozensets."
        bad_terminals_msg = "There are no terminals in the rule dictionary values." 
        bad_start_msg = "Start variable not in the CFG's variable set."
        bad_value_members_msg = "Value member '2' is not a string."

        rules1 = ['dog', 'cat']
        rules2 = self.rules1.copy()
        rules2[0] = 'B'
        rules3 = self.rules1.copy()
        rules3['C'] = '#'
        rules3['D'] = '01'
        rules4 = {
            'A': {'A', 'B'},
            'B': {'A'}
        }
        rules5 = self.rules1.copy()
        rules5['C'] = {2}

        with self.assertRaisesRegex(ValueError, not_dict_msg):
            CFG(rules1, 'dog')
        with self.assertRaisesRegex(ValueError, bad_variables_msg):
            CFG(rules2, 'A')
        with self.assertRaisesRegex(ValueError, bad_values_msg):
            CFG(rules3, 'A')
        with self.assertRaisesRegex(ValueError, bad_terminals_msg):
            CFG(rules4, 'A')
        with self.assertRaisesRegex(ValueError, bad_start_msg):
            CFG(self.rules1, '#')

unittest.main()