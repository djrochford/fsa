from itertools import product

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
            raise ValueError("Start state is not a member of the fsa's state set.")

    def _good_accept(self):
        bad_accept_states = self.accept_states - self.states
        self._error_message(
            bad_accept_states,
            "Accept state {} is not a member of the fsa's state set.",
            "Accept states {} are not members of the fsa's state set."
        )

    def _good_alphabet(self):
        bad_symbols = {x for x in self.alphabet if not (type(x) is str and len(x) == 1)}
        self._error_message(
            bad_symbols,
            "Symbol {} in the alphabet is not single character string.",
            "Symbols {} in the alphabet are not single character strings."
        )

    def _good_range(self):
        bad_range = { x for x in self.transition_function.values() if type(x) != set or type(x) != frozenset }
        self._error_message(
            bad_range,
            "Value {} in the range of the transition function is not a set.",
            "Values {} in the range of the transition function are not sets."
        )
        transition_range = set().union(*self.transition_function.values())
        also_bad_range = transition_range - self.states
        self._error_message(
            also_bad_range,
            "State {} in the range of the transition function is not in the fsa's state set.",
            "States {} in the range of the transition function are not in the fsa's state set."
        )

    def _good_domain(self):
        bad_pairs = product(self.states, self.alphabet) - self.transition_function.keys()
        self._error_message(
            bad_pairs,
            "Pair {} is missing from transition function domain.",
            "Pairs {} are missing from transition function domain."
        )

    def _error_message(self, bad_set, message_singular, message_plural):
        if bad_set != set():
            quoted_members = {"'{}'".format(x) for x in bad_set}
            if len(quoted_members) == 1:
                raise ValueError(message_singular.format(*quoted_members));
            else:
                raise ValueError(message_plural.format((", ").join(quoted_members)))

    def accepts(self, string):
        """Determines whether nfa accepts input string. Will raise a ValueError exception is the string contains
        symbols that aren't in the nfa's alphabet."""
        self._check_input(string)
        get_successor = lambda state, symbol : self.transition_function.get((state, symbol), set())
        get_successors = lambda state_set, symbol: set().union(*{get_successor(state, symbol) for state in state_set})
        def add_epsilons(state_set):
            epsilon_neighbours = get_successors(state_set, '')
            while epsilon_neighbours - state_set != set():
                state_set = state_set | epsilon_neighbours
                epislon_neighbours = get_symbol_successors(epsilon_neighbours, '') 
            return state_set
        current_states = add_epsilons({self.start_state})
        for symbol in string:
            current_states = add_epsilons(get_successors(current_states, symbol))
        return False if current_states & self.accept_states == set() else True

    def _check_input(self, string):
        bad_symbols = set(list(string)) - self.alphabet
        self._error_message(
            bad_symbols,
            "Symbol {} not in fsa's alphabet",
            "Symbols {} not in fsa's alphabet"
        )


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
        self._error_message(
            bad_range,
            "State {} in the range of the transition function is not in the fsa's state set.",
            "States {} in the range of the transition function are not in the fsa's state set."
        )

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
        recognizes A union B. The states of dfa1 | dfa2 are ordered pairs of states from dfa1 and dfa2.

        Except for the caveat below, there is no problem with the input DFAs having different alphabets.

        The function will throw an error if *both* of the following conditions hold:
            1. The alphabet of dfa1 contains symbols that are not in the alphabet of dfa2
            2. `None` is a state of dfa1
        This is because, when condition 1 holds, `None` is used internally for a special purpose
        that breaks if condition 2 holds."""
        union_alphabet = self.alphabet | dfa.alphabet
        def maybe_add_state(dfa1, dfa2):
            new_tf = dfa1.transition_function.copy()
            new_states = dfa1.states.copy()
            extra_symbols = dfa2.alphabet - dfa1.alphabet
            if extra_symbols != set():
                if None in dfa1.states:
                    ordinal1 = "first" if dfa1 == self else "second"
                    ordinal2 = "second" if dfa1 == self else "first"
                    raise ValueError("The alphabet of the {} DFA has symbols that are not in the alphabet of the {} DFA, " \
                        "and the {} DFA has `None` among its states. That's not allowed.".format(ordinal2, ordinal1, ordinal1))
                else:
                    new_states = dfa1.states | {None}
                    for symbol in union_alphabet:
                        new_tf[(None, symbol)] = None
                    for symbol in extra_symbols:
                        for state in dfa1.states:
                            new_tf[(state, symbol)] = None
            return new_states, new_tf
        self_states, self_tf = maybe_add_state(self, dfa)
        other_states, other_tf = maybe_add_state(dfa, self)
        union_states = product(self_states, other_states)
        union_transition_function = {}
        for pair in product(union_states, union_alphabet):
            (state1, state2), symbol = pair
            union_transition_function[pair] = (self_tf[(state1, symbol)], other_tf[(state2, symbol)])
        union_start_state = (self.start_state, dfa.start_state)
        union_accept_states = set(product(self.accept_states, other_states)) | set(product(self_states, dfa.accept_states))
        return DFA(union_transition_function, union_start_state, union_accept_states)

    @staticmethod
    def determinize(nfa):
        """Takes an nfa as input, returns a dfa that recognises the same language as the given nfa. It uses the power-set construction."""
        #powerset function defined at https://docs.python.org/3/library/itertools.html#itertools-recipes
        # def powerset(iterable):
        #     s = list(iterable)
        #     return it.chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
        # determinized_states = powerset(nfa.states)
        # determinized_alphabet = nfa.alphabet
