import itertools as it
import functools as ft

class NFA:
    """A nondeterministic finite automaton class. Takes three parameters: a transition function, a start state 
    and a set of accept states, in that order.

    The transition function should be specified as a dictionary with tuple keys. 
    These keys implicitly define the nfa's state-set and alphabet; the first elements of the tuples represent the
    nfa's states, and the second elements are the symbols in the alphabet.

    The nfa expects the symbols of the alphabet to be one character strings. States can be anything hashable. (Note that,
    for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

    The domain of the transition function is the power-set of the nfa's state set --- i.e., the values of the transition function
    dictionary should be sets. The empty set is a valid value; in fact, you are required to specify that the successor set
    for a given state-symbol pair is the empty set, if it is.

    You can define epsilon-moves by using the empty string in place of an alphabet symbol in the transition function.
    Note that the empty string will not be inferred to be a member of the alphabet (and hence the checks below will work as
    you would expect).

    The class will raise a ValueError exception on instantiation if any of the following are true:
        1. the start state is not a member of the set of states inferred from the transition function;
        2. the set of accept states is not a subset of the set of states inferred from the transition function;
        3. a member of the alphabet inferred from the transition function is not a one-character string;
        4. a member of the transition function's range is not a set;
        5. the range of the transition function is not a subset of the power set of states inferred from the transition function.
        6. The transition function is missing cases -- i.e., it is not the case that every pair of a state and a symbol
        is in the domain of the transition function.
    The exception message will specify which of these four conditions things triggered the exception, and which states/symbols
    are the source of the problem."""

    def __init__(self, transition_function, start_state, accept_states):
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = accept_states
        self.states, self.alphabet = self._extract_states_alphabet(transition_function)
        self._well_defined()

    def _extract_states_alphabet(self, transition_function):
        [states_tuple, alphabet_tuple] = zip(*transition_function.keys())
        states = set(states_tuple)
        alphabet = set(alphabet_tuple) - {""}
        return (states, alphabet)


    def _well_defined(self):
        self._good_start()
        self._good_accept()
        self._good_alphabet()
        self._good_range()
        self._good_domain()

    def _good_start(self):
        if self.start_state not in self.states:
            raise ValueError("Start state not a member of the fsa's state set.")

    def _good_accept(self):
        non_state_accepts = self.accept_states - self.states
        if non_state_accepts != set():
            raise ValueError("Accept states {} not members of the fsa's state set.".format(*non_state_accepts))

    def _good_alphabet(self):
        for symbol in self.alphabet:
            if not (type(symbol) is str and len(symbol) == 1):
                raise ValueError("Symbol {} in the alphabet is not a single character string".format(symbol))

    def _good_range(self):
        not_sets = { x for x in self.transition_function.values() if type(x) != set }
        if not_sets != set():
            raise ValueError("Values {} in the range of the transition function are not sets.".format(*not_sets))
        transition_range = set().union(*self.transition_function.values())
        bad_range = transition_range - self.states
        if bad_range != set():
            raise ValueError("States {} in the range of the transition function are not in the fsa's state set.".format(*bad_range))


    def _good_domain(self):
        missing_pairs = it.product(self.states, self.alphabet) - self.transition_function.keys()
        if missing_pairs != set():
            raise ValueError("Pairs {} missing from transition function domain.".format(*missing_pairs))

    def accepts(self, string):
        """Determines whether nfa accepts input string. Will raise a ValueError exception is the string contains
        symbols that aren't in the nfa's alphabet."""
        self._check_input(string)

        def transition(symbol, state):
            key = (state, symbol)
            if key in self.transition_function.keys():
                return_set = self.transition_function[key]
            else:
                return_set = set()
            return return_set
        get_symbol_successors = lambda state_set, symbol: set().union(*map(ft.partial(transition, symbol), state_set))
        def add_epsilons(state_set):
            epsilon_neighbours = get_symbol_successors(state_set, '')
            while epsilon_neighbours - state_set != set():
                state_set = state_set | epsilon_neighbours
                epislon_neighbours = get_symbol_successors(epsilon_neighbours, '') 
            return state_set
        
        current_states = add_epsilons({self.start_state})
        for symbol in string:
            current_states = get_symbol_successors(current_states, symbol)
            current_states = add_epsilons(current_states)
        return False if current_states & self.accept_states == set() else True

    def _check_input(self, string):
        non_alphabet_symbols = set(list(string)) - self.alphabet
        if non_alphabet_symbols != set():
            raise ValueError("Symbols {} not in fsa's alphabet".format(*non_alphabet_symbols))


class DFA(NFA):
    """A deterministic finite automaton class. Takes three parameters: a transition function, a start state 
    and a set of accept states, in that order.

    The transition function should be specified as a dictionary with tuple keys. 
    These keys implicitly define the dfa's state-set and alphabet; the first elements of the tuples represent the
    fsa's states, and the second elements are the symbols in the alphabet.

    The dfa expects the symbols of the alphabet to be one character strings. States can be anything hashable. (Note that,
    for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)
    
    The class will raise a ValueError exception on instantiation if any of the following are true:
        1. the start state is not a member of the set of states inferred from the transition function;
        2. the set of accept states is not a subset of the set of states inferred from the transition function;
        3. the range of the transition function is not a subset of the set of states inferred from the transition function.
        4. A member of the alphabet inferred from the transition function is not a one-character string.
        5. The transition function is missing a case -- i.e., it is not the case that every pair of a state and a symbol
        is in the domain of the transition function.
    The exception message will specify which of these four conditions things triggered the exception, and which states/symbols
    are the source of the problem."""

    def _good_range(self):
        transition_range = set(self.transition_function.values())
        bad_range = transition_range - self.states
        if bad_range != set():
            raise ValueError("States {} in the range of the transition function are not in the fsa's state set.".format(*bad_range))


    def accepts(self, string):
        """Determines whether dfa accepts input string. Will raise a ValueError exception is the string contains
        symbols that aren't in the dfa's alphabet."""
        self._check_input(string)
        current_state = self.start_state
        for symbol in string:
            current_state = self.transition_function[(current_state, symbol)]
        return False if current_state not in self.accept_states else True

    def __or__(self, dfa):
        """Let A be the language recognised by dfa1, and B be the language recognized by dfa2. `dfa1 | dfa2` returns a dfa that 
        recognizes A union B."""
        union_states = it.product(self.states, dfa.states)
        union_alphabet = self.alphabet | dfa.alphabet
        union_transition_function = {}
        for pair in it.product(union_states, union_alphabet):
            (state1, state2), symbol = pair
            union_transition_function[pair] = (self.transition_function[(state1, symbol)], dfa.transition_function[(state2, symbol)])
        union_start_state = (self.start_state, dfa.start_state)
        union_accept_states = set(it.product(self.accept_states, dfa.states)) | set(it.product(self.states, dfa.accept_states))
        return DFA(union_transition_function, union_start_state, union_accept_states)

    @staticmethod
    def determinize(nfa):
        """Takes an nfa as input, returns a dfa that recognises the same language as the given nfa."""
        #powerset function defined at https://docs.python.org/3/library/itertools.html#itertools-recipes
        def powerset(iterable):
            s = list(iterable)
            return it.chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
        determinized_states = powerset(nfa.states)
        # determinized_alphabet = 

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
    ('q1', '0'): {'q1'},
    ('q1', '1'): {'q1', 'q2'},
    ('q2', '0'): {'q3'},
    ('q2', '1'): {'q3'},
    ('q3', '0'): {'q4'},
    ('q3', '1'): {'q4'},
    ('q4', '0'): set(),
    ('q4', '1'): set(),
}

n2_transition = {
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

m_1 = DFA(m1_transition, 'q1', {'q2'})
m_2 = DFA(m2_transition, 'q1', {'q1'})
m_3 = m_1 | m_2

n_1 = NFA(n1_transition, 'q1', {'q4'})
n_2 = NFA(n2_transition, 'q1', {'q4'})

print(m_1.accepts('101'), m_1.accepts('1000'), m_2.accepts('101'), m_2.accepts('1000'))
print(m_3.accepts('101'), m_3.accepts('1000'))

print(n_1.accepts('00100'), n_1.accepts('0011'), n_2.accepts('00100'), n_2.accepts('0011'))
