import itertools as it
import unittest

class FSA:
    """A finite-state automaton class. Takes three parameters: a transition function, a start state 
    and a set of accept states, in that order.

    The transition function should be specified as a dictionary with tuple keys. 
    These keys implicitly define the fsa's state-set and alphabet; the first elements of the tuples represent the
    fsa's states, and the second elements are the symbols in the alphabet.

    The fsa expects the symbols of the alphabet to be one character strings. States can be anything hashable.

    You can define both deterministic and non-deterministic state machines -- i.e., the domain of the transition function
    can be either the fsa's state-set or the power-set of the fsa's state-set. 
    You can use either a state or its singleton set interchangeable as a value of the transition function;
    they are treated as equivalent.

    The class will raise a ValueError exception on instantiation if any of the following are true:
        1. the start state is not a member of the set of states inferred from the transition function;
        2. the set of accept states is not a subset of the set of states inferred from the transition function;
        3. the range of the transition function is not a subset of the set of states inferred from the transition function.
        4. A member of the alphabet inferred from the transition function is not a one-character string.
        5. The transition function is missing cases -- i.e., it is not the case that every pair of a state and a symbol
        is in the domain of the transition function.
    The exception message will specify which of these four conditions things triggered the exception, and which states/symbols
    are the source of the problem."""

    def __init__(self, transition_function, start_state, accept_states):
        self.start_state = start_state
        self.accept_states = accept_states
        self.states, self.alphabet = self._extract_states_alphabet(transition_function)
        self.transition_function = self._generalize_transition_function(transition_function)
        self._well_defined()

    def __or__(self, fsa):
        """Takes an fsa instance as a parameter. Returns an fsa instance that recognizes the language A union B, 
        where A is the language recognized byself and B the language recognized by the input fsa."""
        union_states = it.product(self.states, fsa.states)
        union_alphabet = self.alphabet | fsa.alphabet
        union_transition_function = {}
        for pair in it.product(union_states, union_alphabet):
            (state1, state2), symbol = pair
            successors = set(it.product(self.transition_function[(state1, symbol)], fsa.transition_function[(state2, symbol)]))
            union_transition_function[pair] = successors
        union_start_state = (self.start_state, fsa.start_state)
        union_accept_states = set(it.product(self.accept_states, fsa.states)) | set(it.product(self.states, fsa.accept_states))
        return FSA(union_transition_function, union_start_state, union_accept_states)

    def _extract_states_alphabet(self, transition_function):
        [states_tuple, alphabet_tuple] = zip(*transition_function.keys())
        return (set(states_tuple), set(alphabet_tuple))

    def _generalize_transition_function(self, transition_function):
        for key, value in transition_function.items():
            if value in self.states:
                transition_function[key] = {value}
        return transition_function

    def _well_defined(self):
        if self.start_state not in self.states:
            raise ValueError("Start state not a member of the fsa's state set.")
        non_state_accepts = self.accept_states - self.states
        if non_state_accepts != set():
            raise ValueError("Accept states {} not members of the fsa's state set.".format(*non_state_accepts))
        transition_range = set()
        for value in self.transition_function.values():
            print ("value:", value)
            if type(value) is set:
                transition_range = transition_range | value
            else: transition_range.add(value)
        non_state_range = transition_range - self.states
        if non_state_range != set():
            raise ValueError("States {} in the range of the transition function are not in the fsa's state set.".format(*non_state_range))
        for symbol in self.alphabet:
            if not (type(symbol) is str and len(symbol) == 1):
                raise ValueError("Symbol {} in the alphabet is not a single character string".format(symbol))
        missing_pairs = it.product(self.states, self.alphabet) - self.transition_function.keys()
        if missing_pairs != set():
            raise ValueError("Pairs {} missing from transition function domain.".format(*missing_pairs))


    def accepts(self, string):
        """Determines whether fsa accepts input string. Will raise a ValueError exception is the string contains
        symbols that aren't in the fsa's alphabet."""
        non_alphabet_symbols = set(list(string)) - self.alphabet
        if non_alphabet_symbols != set():
            raise ValueError("Symbols {} not in fsa's alphabet".format(non_alphabet_symbols))
        current_states = {self.start_state}
        next_states = set()
        for symbol in string:
            next_states = set()
            for state in current_states:
                 next_states = next_states | self.transition_function[(state, symbol)]
            current_states = next_states
        return False if current_states & self.accept_states == set() else True

m1_transition = {
    ('q1', '0'): 'q1',
    ('q1', '1'): 'q2',
    ('q2', '0'): 'q3',
    ('q2', '1'): 'q2',
    ('q3', '0'): 'q2',
    ('q3', '1'): 'q2',
}

m2_transition = {
    ('q1', '0'): 'q1',
    ('q1', '1'): 'q2',
    ('q2', '0'): 'q1',
    ('q2', '1'): 'q2',
}

n1_transition = {
    ('q1', '0'): 'q1',
    ('q1', '1'): {'q1', 'q2'},
    ('q2', '0'): {'q3'},
    ('q2', '1'): 'q3',
    ('q3', '0'): 'q4',
    ('q3', '1'): 'q4',
    ('q4', '0'): set(),
    ('q4', '1'): set()
}

m_1 = FSA(m1_transition, 'q1', {'q2'})
m_2 = FSA(m2_transition, 'q1', {'q1'})
m_3 = m_1 | m_2

n_1 = FSA(n1_transition, 'q1', {'q4'})

print(m_1.accepts('101'), m_1.accepts('1000'), m_2.accepts('101'), m_2.accepts('1000'))
print(m_3.accepts('101'), m_3.accepts('1000'))

print(n_1.accepts('00100'), n_1.accepts('0011'))
