import unittest
from fsa import DFA

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
        bad_start_msg = "Start state is not a member of the fsa's state set."
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
        
        # with self.assertRaisesRegex(ValueError, )

# class TestNFA(unittest.TestCase):

#     def setUp(self):
#         self.tf1 = {
#             ('q1', '0'): {'q1'},
#             ('q1', '1'): {'q1', 'q2'},
#             ('q2', '0'): {'q3'},
#             ('q2', '1'): {'q3'},
#             ('q3', '0'): {'q4'},
#             ('q3', '1'): {'q4'},
#             ('q4', '0'): set(),
#             ('q4', '1'): set(),
#         }

#     def test_instantiation(self):
#         bad_start_msg = "Start state is not a member of the fsa's state set."
#         bad_accept_msg = "Accept states ('bad1', 'bad2'|'bad2', 'bad1') are not members of the fsa's state set."
#         bad_alphabet_msg = "Symbols ('!#', '0'|'0', '!#') in the alphabet are not single character strings."
#         bad_range_msg = "State 'bad' in the range of the transition function is not in the fsa's state set."
#         bad_domain_msg = "Pair '\('q3', '1'\)' is missing from transition function domain."



unittest.main()


# n1_transition = {
#     ('q1', '0'): {'q1'},
#     ('q1', '1'): {'q1', 'q2'},
#     ('q2', '0'): {'q3'},
#     ('q2', '1'): {'q3'},
#     ('q3', '0'): {'q4'},
#     ('q3', '1'): {'q4'},
#     ('q4', '0'): set(),
#     ('q4', '1'): set(),
# }

# n2_transition = {
#     ('q1', '0'): {'q1'},
#     ('q1', '1'): {'q1', 'q2'},
#     ('q2', '0'): {'q3'},
#     ('q2', '1'): set(),
#     ('q2', ''): {'q3'},
#     ('q3', '0'): set(),
#     ('q3', '1'): {'q4'},
#     ('q4', '0'): {'q4'},
#     ('q4', '1'): {'q4'}
# }

# m_1 = DFA(m1_transition, 'q1', {'q2'})
# m_2 = DFA(m2_transition, 'q1', {'q1'})
# m_3 = m_1 | m_2

# n_1 = NFA(n1_transition, 'q1', {'q4'})
# n_2 = NFA(n2_transition, 'q1', {'q4'})

# print(m_1.accepts('101'), m_1.accepts('1000'), m_2.accepts('101'), m_2.accepts('1000'))
# print(m_3.accepts('101'), m_3.accepts('1000'))

# print(n_1.accepts('00100'), n_1.accepts('0011'), n_2.accepts('00100'), n_2.accepts('0011'))