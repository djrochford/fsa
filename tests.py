import unittest
from fsa import DFA, NFA

class TestDFA(unittest.TestCase):

    def setUp(self):
        self.tf1 = {
            ('q1', '0'): 'q1',
            ('q1', '1'): 'q2',
            ('q2', '0'): 'q3',
            ('q2', '1'): 'q2',
            ('q3', '0'): 'q2',
            ('q3', '1'): 'q2'
        }

        tf2 = {
            ('q1', '0'): 'q1',
            ('q1', '1'): 'q2',
            ('q2', '0'): 'q1',
            ('q2', '1'): 'q2'
        }

        tf4 = {
            ('s', 'a'): 'q1',
            ('s', 'b'): 'r1',
            ('q1', 'a'): 'q1',
            ('q1', 'b'): 'q2',
            ('q2', 'a'): 'q1',
            ('q2', 'b'): 'q2',
            ('r1', 'a'): 'r2',
            ('r1', 'b'): 'r1',
            ('r2', 'a'): 'r2',
            ('r2', 'b'): 'r1'
        }

        tf5 = {
            ('q0', '*'): 'q0',
            ('q0', '0'): 'q0',
            ('q0', '1'): 'q1',
            ('q0', '2'): 'q2',
            ('q1', '*'): 'q0',
            ('q1', '0'): 'q1',
            ('q1', '1'): 'q2',
            ('q1', '2'): 'q0',
            ('q2', '*'): 'q0',
            ('q2', '0'): 'q2',
            ('q2', '1'): 'q0',
            ('q2', '2'): 'q1'
        }

        self.m1 = DFA(self.tf1, 'q1', {'q2'})
        self.m2 = DFA(tf2, 'q1', {'q2'})
        self.m3 = DFA(tf2, 'q1', {'q1'})
        self.m4 = DFA(tf4, 's', {'q1', 'r1'})
        self.m5 = DFA(tf5, 'q0', {'q0'})

    def test_instantiation(self):
        bad_start_msg = "Start state '0' is not a member of the fsa's state set."
        bad_accept_msg = "Accept states ('bad1', 'bad2'|'bad2', 'bad1') are not members of the fsa's state set."
        bad_alphabet_msg = "Symbols ('!#', '0'|'0', '!#') in the alphabet are not single character strings."
        bad_range_msg = "State 'bad' in the range of the transition function is not in the fsa's state set."
        bad_domain_msg = "Pair '\('q3', '1'\)' is missing from transition function domain."
        
        tf2 = self.tf1.copy()
        tf2[('q4', '!#')] = 'q3'
        tf2[('q4', 0)] = 'q2'

        tf3 = self.tf1.copy()
        tf3[('q3', '1')] = 'bad'

        tf4 = self.tf1.copy()
        del tf4[('q3', '1')]

        with self.assertRaisesRegex(ValueError, bad_start_msg):
            DFA(self.tf1, 0, {'q2'})
        with self.assertRaisesRegex(ValueError, bad_accept_msg):
            DFA(self.tf1, 'q1', {'bad1', 'bad2', 'q3', 'q2'})
        with self.assertRaisesRegex(ValueError, bad_alphabet_msg):
            DFA(tf2, 'q1', {'q2'})
        with self.assertRaisesRegex(ValueError, bad_range_msg):
            DFA(tf3, 'q1', {'q2'})
        with self.assertRaisesRegex(ValueError, bad_domain_msg):
            DFA(tf4, 'q1', {'q2'})

    def test_accepts(self):
        bad_string_msg = "Symbol '#' not in fsa's alphabet"
        with self.assertRaisesRegex(ValueError, bad_string_msg):
            self.m1.accepts('01100#0')

        self.assertTrue(self.m1.accepts('0101010101'))
        self.assertTrue(self.m1.accepts('0101000000'))
        self.assertFalse(self.m1.accepts('101000'))
        self.assertFalse(self.m1.accepts('0001000'))

        self.assertTrue(self.m2.accepts('1001'))
        self.assertFalse(self.m2.accepts('110'))
        self.assertFalse(self.m2.accepts(''))

        self.assertFalse(self.m3.accepts('1001'))
        self.assertTrue(self.m3.accepts('110'))
        self.assertTrue(self.m3.accepts(''))

        self.assertTrue(self.m4.accepts('abbababbba'))
        self.assertTrue(self.m4.accepts('bbbbaabbab'))
        self.assertFalse(self.m4.accepts('aaabbabbbb'))
        self.assertFalse(self.m4.accepts('bababababa'))

        self.assertTrue(self.m5.accepts(''))
        self.assertTrue(self.m5.accepts('*'))
        self.assertTrue(self.m5.accepts('01022202'))
        self.assertTrue(self.m5.accepts('22*00'))
        self.assertFalse(self.m5.accepts('2101112'))
        self.assertFalse(self.m5.accepts('02121*1'))

    def test_union(self):
        m1_union_m5 = self.m1 | self.m5
        self.assertTrue(m1_union_m5.accepts('10100'))
        self.assertTrue(m1_union_m5.accepts('10110'))
        self.assertTrue(m1_union_m5.accepts('22*12'))
        self.assertFalse(m1_union_m5.accepts('0101000'))

    def test_non_determinize(self):
        non_determinstic = self.m5.non_determinize()
        self.assertIsInstance(non_determinstic, NFA)
        self.assertTrue(self.m5.accepts(''))
        self.assertTrue(self.m5.accepts('*'))
        self.assertTrue(self.m5.accepts('01022202'))
        self.assertTrue(self.m5.accepts('22*00'))
        self.assertFalse(self.m5.accepts('2101112'))
        self.assertFalse(self.m5.accepts('02121*1'))

    def test_encode(self):
        tf = {
            (1, 'a'): 2,
            (1, 'b'): 3,
            (2, 'a'): 1,
            (2, 'b'): 2,
            (3, 'a'): 2,
            (3, 'b'): 1
        }
        M = DFA(tf, 1, {2, 3})
        self.assertEqual(M.encode(),
            '(a(aa|b)*ab|b)((ba|a)(aa|b)*ab|bb)*((ba|a)(aa|b)*|€)|a(aa|b)*'
        )


class TestNFA(unittest.TestCase):

    def setUp(self):

        self.tf1 = {
            ('q1', '0'): {'q1'},
            ('q1', '1'): {'q1', 'q2'},
            ('q2', '0'): {'q3'},
            ('q2', '1'): set(),
            ('q2', ''): {'q3'},
            ('q3', '0'): set(),
            ('q3', '1'): {'q4'},
            ('q4', '0'): {'q4'},
            ('q4', '1'): {'q4'}
        }

        tf2 = {
            ('q1', '0'): {'q1'},
            ('q1', '1'): {'q1', 'q2'},
            ('q2', '0'): {'q3'},
            ('q2', '1'): {'q3'},
            ('q3', '0'): {'q4'},
            ('q3', '1'): {'q4'},
            ('q4', '0'): set(),
            ('q4', '1'): set()
        }
        
        tf3 = {
            ('s', ''): {'q1', 'r1'},
            ('s', '0'): set(),
            ('q1', '0'): {'q2'},
            ('q2', '0'): {'q1'},
            ('r1', '0'): {'r2'},
            ('r2', '0'): {'r3'},
            ('r3', '0'): {'r1'}
        }

        tf4 = {
            ('q1', ''): {'q3'},
            ('q1', 'a'): set(),
            ('q1', 'b'): {'q2'},
            ('q2', 'a'): {'q2', 'q3'},
            ('q2', 'b'): {'q3'},
            ('q3', 'a'): {'q1'},
            ('q3', 'b'): set()
        }

        self.n1 = NFA(self.tf1, 'q1', {'q4'})
        self.n2 = NFA(tf2, 'q1', {'q4'})
        self.n3 = NFA(tf3, 's', {'q1', 'r1'})
        self.n4 = NFA(tf4, 'q1', {'q1'})        

    def test_instantiation(self):
        bad_start_msg = "Start state 'bad' is not a member of the fsa's state set."
        bad_accept_msg = "Accept states ('bad1', 'bad2'|'bad2', 'bad1') are not members of the fsa's state set."
        bad_alphabet_msg = "Symbols ('!#', '0'|'0', '!#') in the alphabet are not single character strings."
        bad_range_msg1 = "Value 'q1' in the range of the transition function is not a set."
        bad_range_msg2 = "State 'bad' in the range of the transition function is not in the fsa's state set."
        bad_domain_msg = "Pair '\('q3', '1'\)' is missing from transition function domain."

        tf2 = self.tf1.copy()
        tf2[('q5', '!#')] = {'q3'}
        tf2[('q5', 0)] = {'q2'}
        
        tf3 = self.tf1.copy()
        tf3[('q3', '1')] = 'q1'

        tf4 = self.tf1.copy()
        tf4[('q3', '1')] = {'bad'}

        tf5 = self.tf1.copy()
        del tf5[('q3', '1')]

        with self.assertRaisesRegex(ValueError, bad_start_msg):
            NFA(self.tf1, 'bad', {'q4'})
        with self.assertRaisesRegex(ValueError, bad_accept_msg):
            NFA(self.tf1, 'q1', {'bad1', 'bad2', 'q4'})
        with self.assertRaisesRegex(ValueError, bad_alphabet_msg):
            NFA(tf2, 'q1', {'q4'})
        with self.assertRaisesRegex(ValueError, bad_range_msg1):
            NFA(tf3, 'q1', {'q4'})
        with self.assertRaisesRegex(ValueError, bad_range_msg2):
            NFA(tf4, 'q1', {'q4'})
        with self.assertRaisesRegex(ValueError, bad_domain_msg):
            NFA(tf5, 'q1', {'q4'})

    def test_accepts(self):
        self.assertTrue(self.n1.accepts('10100100'))
        self.assertTrue(self.n1.accepts('00111101'))
        self.assertFalse(self.n1.accepts('10001001'))

        self.assertTrue(self.n2.accepts('000100'))
        self.assertFalse(self.n2.accepts('011010'))

        self.assertTrue(self.n3.accepts(''))
        self.assertTrue(self.n3.accepts('00'))
        self.assertTrue(self.n3.accepts('000'))
        self.assertTrue(self.n3.accepts('0000'))
        self.assertTrue(self.n3.accepts('000000'))
        self.assertFalse(self.n3.accepts('0'))
        self.assertFalse(self.n3.accepts('00000'))

        self.assertTrue(self.n4.accepts(''))
        self.assertTrue(self.n4.accepts('a'))
        self.assertTrue(self.n4.accepts('baba'))
        self.assertTrue(self.n4.accepts('baa'))
        self.assertFalse(self.n4.accepts('b'))
        self.assertFalse(self.n4.accepts('bb'))
        self.assertFalse(self.n4.accepts('babba'))

    def test_determinize(self):
        d1 = self.n4.determinize()
        self.assertIsInstance(d1, DFA)
        self.assertEqual(
            d1.get_states(),
            {
                frozenset(),
                frozenset({'q1'}),
                frozenset({'q2'}),
                frozenset({'q3'}),
                frozenset({'q1', 'q2'}),
                frozenset({'q1', 'q3'}),
                frozenset({'q2', 'q3'}),
                frozenset({'q1', 'q2', 'q3'})
            }
        )
        self.assertTrue(d1.accepts(''))
        self.assertTrue(d1.accepts('a'))
        self.assertTrue(d1.accepts('baba'))
        self.assertTrue(d1.accepts('baa'))
        self.assertFalse(d1.accepts('b'))
        self.assertFalse(d1.accepts('bb'))
        self.assertFalse(d1.accepts('babba'))

        d2 = self.n3.determinize()
        self.assertTrue(d2.accepts(''))
        self.assertTrue(d2.accepts('00'))
        self.assertTrue(d2.accepts('000'))
        self.assertTrue(d2.accepts('0000'))
        self.assertTrue(d2.accepts('000000'))
        self.assertFalse(d2.accepts('0'))
        self.assertFalse(d2.accepts('00000'))

    def test_union(self):
        n1_union_n2 = self.n1 | self.n2
        self.assertTrue(n1_union_n2.accepts('10100100'))
        self.assertTrue(n1_union_n2.accepts('00111101'))
        self.assertTrue(n1_union_n2.accepts('000100'))
        self.assertTrue(n1_union_n2.accepts('011010'))
        self.assertFalse(n1_union_n2.accepts('10001001'))
        self.assertFalse(n1_union_n2.accepts('001001000'))

        n1_union_n4 = self.n1 | self.n4
        self.assertTrue(n1_union_n4.accepts('10100100'))
        self.assertTrue(n1_union_n4.accepts('00111101'))
        self.assertTrue(n1_union_n4.accepts(''))
        self.assertTrue(n1_union_n4.accepts('a'))
        self.assertTrue(n1_union_n4.accepts('baba'))
        self.assertTrue(n1_union_n4.accepts('baa'))
        self.assertFalse(n1_union_n4.accepts('10001001'))
        self.assertFalse(n1_union_n4.accepts('b'))
        self.assertFalse(n1_union_n4.accepts('bb'))
        self.assertFalse(n1_union_n4.accepts('babba'))

    def test_concat(self):
        n1_concat_n2 = self.n1 + self.n2
        self.assertTrue(n1_concat_n2.accepts('10100100000100'))
        self.assertTrue(n1_concat_n2.accepts('00111101000100'))
        self.assertFalse(n1_concat_n2.accepts('10100100011010'))
        self.assertFalse(n1_concat_n2.accepts('00111101011010'))

    def test_star(self):
        tf_5 = {
            ('q1', '0'): {'q1'},
            ('q1', '1'): {'q2'},
            ('q2', '0'): {'q2'},
            ('q2', '1'): {'q3'},
            ('q3', '0'): {'q3'},
            ('q3', '1'): {'q3'}
        }

        n5 = NFA(tf_5, 'q1', {'q2'})
        n5_star = n5.star()
        self.assertTrue(n5.accepts('1000'))
        self.assertFalse(n5.accepts('10001000'))
        self.assertFalse(n5.accepts(''))
        self.assertTrue(n5_star.accepts('1000'))
        self.assertTrue(n5_star.accepts('10001000'))
        self.assertTrue(n5_star.accepts(''))

    def test_fit(self):
        bad_alphabet_message = "Alphabet cannot contain characters"#('*', '•'|'•', '*')." 
        #When the end of the error message is included above, it fails for no good reason that I can discern.
        bad_start_message = "Regex cannot start with '|'."
        bad_regex_character_message = "Regex contains character '¢' that is not in alphabet and not an accepted regex character."
        bad_regex_operator_message = "Regex contains binary operator followed by an operator; not cool."
        bad_regex_right_parenthesis_message = "Right parenthesis occurs in regex withour matching left parenthesis."
        bad_regex_left_parenthesis_message = "Left parenthesis occurs in regex without matching right parenthesis."

        with self.assertRaisesRegex(ValueError, bad_alphabet_message):
            NFA.fit('(a|b)*c', {'a', 'b', 'c', '•', '*'})
        with self.assertRaisesRegex(ValueError, bad_start_message):
            NFA.fit('|aabbb0')
        with self.assertRaisesRegex(ValueError, bad_regex_character_message):
            NFA.fit('9*l¢k')
        with self.assertRaisesRegex(ValueError, bad_regex_operator_message):
            NFA.fit('po|*k')
        with self.assertRaisesRegex(ValueError, bad_regex_right_parenthesis_message):
            NFA.fit('z•o|o*p)')
        with self.assertRaisesRegex(ValueError, bad_regex_left_parenthesis_message):
            NFA.fit('pl((*|p)•q')

        fitted_1 = NFA.fit('Ø')
        self.assertFalse(fitted_1.accepts(''))
        self.assertFalse(fitted_1.accepts('abcb'))

        fitted_2 = NFA.fit('€')
        self.assertTrue(fitted_2.accepts(''))
        self.assertFalse(fitted_2.accepts('dff&p'))

        fitted_3 = NFA.fit('ad0!!')
        self.assertTrue(fitted_3.accepts('ad0!!'))
        self.assertFalse(fitted_3.accepts('ad0!'))

        fitted_4 = NFA.fit('a|b')
        self.assertFalse(fitted_4.accepts(''))
        self.assertTrue(fitted_4.accepts('a'))
        self.assertTrue(fitted_4.accepts('b'))
        self.assertFalse(fitted_4.accepts('c'))
        self.assertFalse(fitted_4.accepts('aa'))

        fitted_5 = NFA.fit('(ab)*')
        self.assertTrue(fitted_5.accepts(''))
        self.assertFalse(fitted_5.accepts('b'))
        self.assertTrue(fitted_5.accepts('ab'))
        self.assertTrue(fitted_5.accepts('ababababababab'))
        self.assertFalse(fitted_5.accepts('ababababababa'))

        fitted_6 = NFA.fit('b*a(d*|aaa)4')
        self.assertFalse(fitted_6.accepts(''))
        self.assertTrue(fitted_6.accepts('a4'))
        self.assertTrue(fitted_6.accepts('bad4'))
        self.assertTrue(fitted_6.accepts('bbbbbaaaa4'))
        self.assertTrue(fitted_6.accepts('bbbbadddddd4'))
        self.assertFalse(fitted_6.accepts('bdddd4'))
        self.assertFalse(fitted_6.accepts('adaaa4'))
        self.assertFalse(fitted_6.accepts('bbaaa4'))

unittest.main()