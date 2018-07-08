import unittest
import re
from ..cfg import CFG

class TestCFG(unittest.TestCase):

    def setUp(self):
        self.rules1 = {
            'A': {'0A1', 'B'},
            'B': {'#'}
        }

        rules2 = {
            '<SENTENCE>': {['<NOUN-PHRASE>', ' ', '<VERB-PHRASE>']},
            '<NOUN-PHRASE>': {'<CMPLX-NOUN>', ['<CMPLX-NOUN>', ' ', '<PREP-PHRASE>']},
            '<VERB-PHRASE>': {'<CMPLX-VERB>', ['<CMPLX-VERB>', ' ', '<PREP-PHRASE>']},
            '<PREP-PHRASE>': {['<PREP>', ' ', ' <CMPLX-NOUN>']},
            '<CMPLX-NOUN>': {['<ARTICLE>', ' ', '<NOUN>']},
            '<CMPLX-VERB>': {'<VERB>', ['<VERB>', ' ', '<NOUN-PHRASE>']},
            '<ARTICLE>': {'a', 'the'},
            '<NOUN>': {'boy', 'girl', 'flower'},
            '<VERB>': {'touches', 'likes', 'sees'},
            '<PREP>': {'with'}
        }

        rules3 = {
            'S': {['a', 'S', 'b'], ['S', 'S'], '€'}
        }

        rules4 = {
            '<EXPR>': {['<EXPR>', '+', '<TERM>'], '<TERM>'},
            '<TERM>': {['<TERM>', '*', '<FACTOR>'], '<FACTOR>'},
            '<FACTOR>': {['(', '<EXPR>', ')'], 'a'}
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

    def test_chomsky_normalize(self):
        def parse_substitution(string):
            values = {v for v, s in rule_set} | self.terminals
            parsed = []
            value_candidate = ''
            is_value = False
            for char in string:
                if not re.compile(r'\w').match(char):
                    value_candidate += char
                if value_candidate in values:
                    is_value = True
                else:
                    if is_value:
                        parsed.append(value_candidate[-1])
                        value_candidate = value_candidate[0]
                        is_value = value_candidate in values
            if value_candidate in values:
                parsed.append(value_candidate)
            else:
                raise ValueError ("Error while parsing rule substitution: substitution cannot be parsed into values.")
            return parsed
        
        rules = {
            'S': {'ASA', 'aB'},
            'A': {'B', 'S'},
            'B': {'b', '€'}
        }
        
        non_normal = CFG(rules, 'S')
        protonormal = non_normal.chomsky_normalize()
        #This below is to make sure the normalized grammar is a well-formed grammar, and
        #passes all the checks that occur during instantiation.
        normal = CFG(protonormal.get_rules(), protonormal.get_start_variable())
        normal_rules = normal.get_rules()
        for substitution in set.union(*list(normal_rules.values())):
            substitution_list = parse_substitution(substitution)
            length = len(substitution_list)
            self.assertLessEqual(length, 2)
            self.assertGreater(length, 0)
            if length == 2:
                for char in substitution_list:
                    self.assertIn(char, normal.get_variables() - {normal.get_start_variable()})
            if length == 1:
                char = substitution_list[0]
                self.assertIn(char, normal.get_terminals() | {'€'})







if __name__ == '__main__':
    unittest.main()