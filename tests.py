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
        
        bad_union_message = "The alphabet of the second DFA has symbols that are not in the alphabet of the first DFA, " \
            "and the first DFA has `None` among its states. That's not allowed."
        tf2 = self.tf1.copy()
        tf2[(None, '0')] = 'q1'
        tf2[(None, '1')] = 'q2'
        m2 = DFA(tf2, 'q1', {'q2'})
        with self.assertRaisesRegex(ValueError, bad_union_message):
            bad_union = m2 | self.m5

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

    def test_copy(self):
        n1_copy = self.n1.copy()
        self.assertEqual(
            n1_copy.get_states(),
            {'q1`', 'q2`', 'q3`', 'q4`'}
        )
        self.assertTrue(self.n1.accepts('10100100'))
        self.assertTrue(self.n1.accepts('00111101'))
        self.assertFalse(self.n1.accepts('10001001'))



unittest.main()