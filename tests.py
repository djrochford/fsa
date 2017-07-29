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

    def test_instantiation(self):
        bad_start_msg = "Start state is not a member of the fsa's state set."
        bad_accept_msg = "Accept states ('bad1', 'bad2'|'bad2', 'bad1') are not members of the fsa's state set."
        bad_alphabet_msg = "Symbols ('!#', '0'|'0', '!#') in the alphabet are not single character strings."
        bad_range_msg = "State 'bad' in the range of the transition function is not in the fsa's state set."
        
        tf2 = self.tf1.copy()
        tf2[('q4', '!#')] = 'q3'
        tf2[('q4', 0)] = 'q2'

        tf3 = self.tf1.copy()
        tf3[('q3', '1')] = 'bad'

        with self.assertRaisesRegex(ValueError, bad_start_msg):
            DFA(self.tf1, 0, {'q3'})
        with self.assertRaisesRegex(ValueError, bad_accept_msg):
            DFA(self.tf1, 'q1', {'bad1', 'bad2', 'q3', 'q2'})
        with self.assertRaisesRegex(ValueError, bad_alphabet_msg):
            DFA(tf2, 'q1', {'q3'})
        with self.assertRaisesRegex(ValueError, bad_range_msg):
            DFA(tf3, 'q1', {'q3'})
        # with self.assertRaisesRegex(ValueError, )


unittest.main()

# m2_transition = {
#     ('q1', '0'): 'q1',
#     ('q1', '1'): 'q2',
#     ('q2', '0'): 'q1',
#     ('q2', '1'): 'q2',
# }
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