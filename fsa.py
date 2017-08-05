from itertools import product, chain, combinations

class _Base:

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
            raise ValueError("Start state '{}' is not a member of the fsa's state set.".format(self.start_state))

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

    def _check_input(self, string):
        bad_symbols = set(list(string)) - self.alphabet
        self._error_message(
            bad_symbols,
            "Symbol {} not in fsa's alphabet",
            "Symbols {} not in fsa's alphabet"
        )

    def _get_other_state(self, state_set):
        other_state = 'new_state'
        while other_state in state_set:
            other_state = other_state + '`'
        return other_state

    def get_states(self):
        return self.states.copy()

    def get_alphabet(self):
        return self.alphabet.copy()

    def get_transition_function(self):
        return self.transition_function.copy()

    def get_start_state(self):
        return self.start_state

    def get_accept_states(self):
        return self.accept_states.copy()


class NFA(_Base):
    """A nondeterministic finite automaton class. Takes three parameters: a transition function, a start state 
    and a set of accept states, in that order.

    The transition function should be specified as a dictionary with tuple keys. 
    These keys implicitly define the nfa's state-set and alphabet; the first elements of the tuples represent the
    nfa's states, and the second elements are the symbols in the alphabet.

    The nfa expects the symbols of the alphabet to be one character strings. States can be anything hashable. (Note that,
    for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

    The domain of the transition function is the power-set of the nfa's state set --- i.e., the values of the transition function
    dictionary should be sets (or frozensets). The empty set is a valid value; in fact, you are required to specify that the successor set
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

    def __or__(self, other):
        """Let A be the language recognised by nfa1, and B be the language recognized by nfa2. `nfa1 | nfa2` returns an nfa that 
        recognizes A union B. The cardinality of the state-set of nfa1 | nfa2 is the cardinality of the state set of nfa1
        plus the cardinality of the state-set of nfa2 plus 1.

        There is no problem with the input NFAs having different alphabets."""
        new_self, new_other = self._prepare_for_combination(other)
        union_tf = {}
        union_tf.update(new_self.transition_function)
        union_tf.update(new_other.transition_function)
        union_start_state = new_self._get_other_state(new_self.states | new_other.states)
        union_tf[(union_start_state, '')] = { new_self.start_state, new_other.start_state }
        for symbol in new_self.alphabet | new_other.alphabet:
            union_tf[(union_start_state, symbol)] = set()
        union_accept_states = new_self.accept_states | new_other.accept_states
        return NFA(union_tf, union_start_state, union_accept_states)

    def __add__(self, other):
        """Let A be the language recognised by nfa1, and B be the language recognized by nfa2. `nfa1 + nfa2` returns an nfa that
        recognizes A concat B -- i.e., the language consisten of the set of strins of the form a concat b, where a is an element of A
        and b is an element of B. Note that a this `+` operation is not commutative."""

        new_self, new_other = self._prepare_for_combination(other)
        concat_tf = {}
        concat_tf.update(new_self.transition_function)
        concat_tf.update(new_other.transition_function)
        for state in new_self.accept_states:
            concat_tf[(state, '')] = {new_other.start_state}
        return NFA(concat_tf, new_self.start_state, new_other.accept_states)

        
    def _prepare_for_combination(self, other):
        def copy(nfa):
            new_to_old = {}
            prime = lambda state : str(state) + '`'
            copy_tf = {}
            for state, symbol in nfa.transition_function.keys():
                copy_tf[(prime(state), symbol)] = { prime(x) for x in nfa.transition_function[(state, symbol)] }
            copy_start = prime(nfa.start_state)
            copy_accept = { prime(x) for x in nfa.accept_states }
            return NFA(copy_tf, copy_start, copy_accept)
        overlap = self.states & other.states
        while overlap != set():
            other = copy(other)
            overlap = self.states & other.states
        def add_empty_transitions(nfa1, nfa2):
            def add_one_way(nfa1, nfa2):
                new_tf = nfa1.transition_function.copy()
                extra_symbols = nfa2.alphabet - nfa1.alphabet
                if extra_symbols != set():
                    for pair in product(nfa1.states, extra_symbols):
                        new_tf[pair] = set()
                return new_tf
            return add_one_way(nfa1, nfa2), add_one_way(nfa2, nfa1)
        self_tf, other_tf = add_empty_transitions(self, other)
        new_self = NFA(self_tf, self.start_state, self.accept_states)
        new_other = NFA(other_tf, other.start_state, other.accept_states)
        return new_self, new_other

    def _good_range(self):
        bad_range = { x for x in self.transition_function.values() if type(x) != set and type(x) != frozenset }
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

    def _get_successors(self, tf, state_set, symbol):
        get_successor = lambda state,  s: tf.get((state, s), set())
        return set().union(*[get_successor(state, symbol) for state in state_set])

    def _add_epsilons(self, tf, state_set):
        epsilon_neighbours = self._get_successors(tf, state_set, '')
        while epsilon_neighbours - state_set != set():
            state_set = state_set | epsilon_neighbours
            epsilon_neighbours = self._get_successors(tf, epsilon_neighbours, '') 
        return state_set

    def _transition(self, tf, state_set, symbol):
        return self._add_epsilons(tf, self._get_successors(tf, state_set, symbol))

    def accepts(self, string):
        """Determines whether nfa accepts input string. Will raise a ValueError exception is the string contains
        symbols that aren't in the nfa's alphabet."""
        self._check_input(string)
        current_states = self._add_epsilons(self.transition_function, {self.start_state})
        for symbol in string:
            current_states = self._transition(self.transition_function, current_states, symbol)
        return False if current_states & self.accept_states == set() else True

    def determinize(self):
        """Returns a DFA that recognizes the same same language as the NFA instance.
        The set of DFA states is the power-set of the set of NFA states."""
        #powerset code an itertools recipe, from https://docs.python.org/3/library/itertools.html#recipes
        #(minor adjustment made to make the result a set)
        def powerset(iterable):
            s = list(iterable)
            return chain.from_iterable(set(combinations(s, r)) for r in range(len(s)+1))
        determinized_states = powerset(self.states)
        determinized_alphabet = self.alphabet
        determinized_tf = {}
        determinized_accept = set()
        for (combination, symbol) in product(determinized_states, determinized_alphabet):
            state = frozenset(combination)
            pair = (state, symbol)
            determinized_tf[pair] = frozenset(self._transition(self.transition_function, *pair))
            if state & self.accept_states != set():
                determinized_accept.add(state)
        determinized_start = frozenset(self._add_epsilons(self.transition_function, {self.start_state}))
        return DFA(determinized_tf, determinized_start, determinized_accept)


class DFA(_Base):
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

    def __or__(self, other):
        """Let A be the language recognised by dfa1, and B be the language recognized by dfa2. `dfa1 | dfa2` returns a dfa that 
        recognizes A union B. The states of dfa1 | dfa2 are ordered pairs of states from dfa1 and dfa2.

        There is no problem with the input DFAs having different alphabets."""

        union_alphabet = self.alphabet | other.alphabet
        def maybe_add_state(dfa1, dfa2):
            new_tf = dfa1.transition_function.copy()
            new_states = dfa1.states.copy()
            extra_symbols = dfa2.alphabet - dfa1.alphabet
            if extra_symbols != set():
                error_state = self._get_other_state(dfa1.states)
                new_states = dfa1.states | { error_state }
                for symbol in union_alphabet:
                    new_tf[(error_state, symbol)] = error_state
                for symbol in extra_symbols:
                    for state in dfa1.states:
                        new_tf[(state, symbol)] = error_state
            return new_states, new_tf
        self_states, self_tf = maybe_add_state(self, other)
        other_states, other_tf = maybe_add_state(other, self)
        union_states = product(self_states, other_states)
        union_transition_function = {}
        for pair in product(union_states, union_alphabet):
            (state1, state2), symbol = pair
            union_transition_function[pair] = (self_tf[(state1, symbol)], other_tf[(state2, symbol)])
        union_start_state = (self.start_state, other.start_state)
        union_accept_states = set(product(self.accept_states, other_states)) | set(product(self_states, other.accept_states))
        return DFA(union_transition_function, union_start_state, union_accept_states)

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


