"""
File containing DFA and NFA public classes
"""
from itertools import product, chain, combinations
from string import printable
from typing import (
    AbstractSet,
    Container,
    FrozenSet,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    Union
)

from .base import (
    _Base,
    _extract_states_alphabet,
    _error_message,
    _good_alphabet,
    _check_input
)


State = str

Symbol = str

Regex = str

FsaTransitionFunction = Mapping[
    Tuple[State, Symbol], Union[State, AbstractSet[State]]
]


class _FSA(_Base):
    def __init__(
            self,
            transition_function: FsaTransitionFunction,
            start_state: State,
            accept_states: AbstractSet[State]
    ):
        super().__init__(
            transition_function=transition_function, start_state=start_state
        )
        self._accept_states = accept_states
        self._states, self._alphabet = _extract_states_alphabet(
            self._transition_function.keys()
        )
        self._well_defined()

    @property
    def alphabet(self) -> FrozenSet[Symbol]:
        return self._alphabet

    @property
    def accept_states(self) -> AbstractSet[State]:
        return self._accept_states

    def _well_defined(self) -> None:
        super()._well_defined()
        _good_alphabet(alphabet=self.alphabet, name="alphabet")
        self._good_accept()
        self._good_domain(self.alphabet)

    def _good_accept(self) -> None:
        bad_accept_states = self.accept_states - self.states
        _error_message(
            bad_set=bad_accept_states,
            message_singular=("Accept state {} is not a member of the fsa's "
                              "state set."),
            message_plural=("Accept states {} are not members of the fsa's "
                            "state set.")
        )

    def _get_new_state(self, state_set: Container) -> State:
        counter = 1
        new_state = 'new_state1'
        while new_state in state_set:
            counter += 1
            new_state = new_state + str(counter)
        return new_state


GnfaTransitionFunction = Mapping[Tuple[State, State], Regex]


class _GNFA:
    def __init__(
            self,
            transition_function: GnfaTransitionFunction,
            body_states: Set[State],
            start_state: State,
            accept_state: State
    ):
        self.transition_function = transition_function
        self.body_states = body_states
        self.start_state = start_state
        self.accept_state = accept_state
        self.states = self.body_states | {self.start_state} | {self.accept_state}

    def reduce(self) -> "_GNFA":
        def union_main_scope(regex: Regex) -> bool:
            paren_count = 0
            for char in regex:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == '|':
                    if paren_count == 0:
                        return True
            return False

        def regex_star(regex: Regex) -> Regex:
            if regex == 'Ø' or regex == '€':
                return_value = '€'
            elif len(regex) == 1:
                return_value = regex + '*'
            else:
                return_value = "({})*".format(regex)
            return return_value

        def regex_concat(regex1: Regex, regex2: Regex) -> Regex:
            if regex1 == 'Ø' or regex2 == 'Ø':
                return_value = 'Ø'
            elif regex1 == '€':
                return_value = regex2
            elif regex2 == '€':
                return_value = regex1
            else:
                if union_main_scope(regex1):
                    regex1 = '({})'.format(regex1)
                if union_main_scope(regex2):
                    regex2 = '({})'.format(regex2)
                return_value = regex1 + regex2
            return return_value

        def regex_union(regex1: Regex, regex2: Regex) -> Regex:
            if regex1 == "Ø":
                return_value = regex2
            elif regex2 == "Ø":
                return_value = regex1
            else:
                return_value = "{}|{}".format(regex1, regex2)
            return return_value

        rip = self.body_states.pop()
        r2 = self.transition_function[(rip, rip)]
        reduced_tf = {}
        for state1 in self.states - {self.accept_state, rip}:
            r1 = self.transition_function[(state1, rip)]
            for state2 in self.states - {self.start_state, rip}:
                r3 = self.transition_function[(rip, state2)]
                r4 = self.transition_function[(state1, state2)]
                new_regex = regex_union(regex_concat(regex_concat(r1, regex_star(r2)), r3), r4)
                reduced_tf[(state1, state2)] = new_regex
        return _GNFA(reduced_tf, self.body_states - {rip}, self.start_state, self.accept_state)


NfaTransitionFunction = Mapping[Tuple[State, Symbol], AbstractSet[State]]
MutableNfaTF = MutableMapping[Tuple[State, Symbol], Set[State]]

class NFA(_FSA):
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
        5. the range of the transition function is not a subset of the power set of states inferred from the transition function;
        6. the transition function is missing cases -- i.e., it is not the case that every pair of a state and a symbol
        is in the domain of the transition function.
    The exception message will specify which of these six conditions things triggered the exception, and which states/symbols
    are the source of the problem."""

    def __or__(self, other: "NFA") -> "NFA":
        """Let A be the language recognised by nfa1, and B be the language recognized by nfa2. `nfa1 | nfa2` returns an nfa that 
        recognizes A union B. The cardinality of the state-set of nfa1 | nfa2 is the cardinality of the state set of nfa1
        plus the cardinality of the state-set of nfa2 plus 1.

        There is no problem with the input NFAs having different alphabets."""
        new_self, new_other, union_tf = self._combine(other)
        union_start_state = self._get_new_state(new_self.states | new_other.states)
        union_tf[(union_start_state, '')] = { new_self.start_state, new_other.start_state }
        for symbol in new_self.alphabet | new_other.alphabet:
            union_tf[(union_start_state, symbol)] = set()
        union_accept_states = new_self.accept_states | new_other.accept_states
        return NFA(union_tf, union_start_state, union_accept_states)

    def __add__(self, other: "NFA") -> "NFA":
        """Let A be the language recognised by nfa1, and B be the language recognized by nfa2. `nfa1 + nfa2` returns an nfa that
        recognizes A concat B -- i.e., the language consisten of the set of strins of the form a concat b, where a is an element of A
        and b is an element of B. Note that a this `+` operation is not commutative."""
        new_self, new_other, concat_tf = self._combine(other)
        for state in new_self.accept_states:
            if (state, '') in concat_tf.keys():
                concat_tf[(state, '')].add(new_other.start_state)
            else:
                concat_tf[(state, '')] = { new_other.start_state }
        return NFA(concat_tf, new_self.start_state, new_other.accept_states)

    def _combine(self, other: "NFA") -> Tuple["NFA", "NFA", MutableNfaTF]:
        def copy(nfa: NFA) -> NFA:
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

        def add_empty_transitions(
                nfa1: NFA, nfa2: NFA
        ) -> Tuple[NfaTransitionFunction, NfaTransitionFunction]:
            def add_one_way(nfa1: NFA, nfa2: NFA) -> NfaTransitionFunction:
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
        combination_tf = {}
        combination_tf.update(new_self.transition_function)
        combination_tf.update(new_other.transition_function)
        return new_self, new_other, combination_tf

    def _good_range(self) -> None:
        bad_range = { x for x in self.transition_function.values() if type(x) != set and type(x) != frozenset }
        _error_message(
            bad_set=bad_range,
            message_singular=("Value {} in the range of the transition "
                              "function is not a set."),
            message_plural=("Values {} in the range of the transition "
                            "function are not sets.")
        )
        transition_range: Set[Optional[AbstractSet[State]]] = set.union(*self.transition_function.values())
        also_bad_range = transition_range - self.states
        _error_message(
            bad_set=also_bad_range,
            message_singular=("State {} in the range of the transition "
                              "function is not in the fsa's state set."),
            message_plural=("States {} in the range of the transition "
                            "function are not in the fsa's state set.")
        )

    def _get_successors(self, state_set: AbstractSet[State], symbol: Symbol) -> FrozenSet[State]:
        get_successor = lambda state,  s: self._transition_function.get((state, s), frozenset())
        empty: FrozenSet[State] = frozenset()
        return empty.union(*[frozenset(get_successor(state, symbol)) for state in state_set])

    def _add_epsilons(self, state_set: AbstractSet[State]) -> AbstractSet[State]:
        epsilon_neighbours = self._get_successors(state_set, '')
        while epsilon_neighbours - state_set != set():
            state_set = state_set | epsilon_neighbours
            epsilon_neighbours = self._get_successors(epsilon_neighbours, '') 
        return state_set

    def _transition(self, state_set: AbstractSet[State], symbol: Symbol):
        return self._add_epsilons(self._get_successors(state_set, symbol))

    def accepts(self, string: str) -> bool:
        """Determines whether nfa accepts input string. Will raise a ValueError exception is the string contains
        symbols that aren't in the nfa's alphabet."""
        _check_input(string=string, alphabet=self.alphabet)
        current_states = self._add_epsilons({self.start_state})
        for symbol in string:
            current_states = self._transition(current_states, symbol)
        return False if current_states & self.accept_states == set() else True

    def determinize(self) -> "DFA":
        """Returns a DFA that recognizes the same same language as the NFA instance.
        WARNING: The set of DFA states is the power-set of the set of NFA states. For related reasons,
        the time complexity of this method is exponential in the number of states of the NFA. 
        Don't determinize big NFAs."""
        # powerset code an itertools recipe, from https://docs.python.org/3/library/itertools.html#recipes
        # (minor adjustment to make the output a set of sets)
        def powerset(iterable: Iterable) -> Set[FrozenSet]:
            s = list(iterable)
            return {frozenset(combo) for combo in chain.from_iterable(combinations(s, r) for r in range(len(s)+1))}
        state_sets = powerset(self.states)
        determinized_tf = {}
        determinized_accept = set()
        for (state_set, symbol) in product(state_sets, self._alphabet):
            determinized_tf[(str(state_set), symbol)] = str(self._transition(state_set, symbol))
            if state_set & self.accept_states:
                determinized_accept.add(str(state_set))
        determinized_start = str(self._add_epsilons({self._start_state}))
        return DFA(determinized_tf, determinized_start, determinized_accept)


    def star(self) -> "NFA":
        """Let A be the language recognised by nfa. `nfa.self()` returns an nfa that recognizes A* --
        i.e., the set of all strings formed by concatenating any number of members of A."""
        star_start = self._get_new_state(self.states)
        star_tf = self.transition_function.copy()
        star_tf[(star_start, '')] = { self.start_state }
        for symbol in self.alphabet:
            star_tf[(star_start, symbol)] = set()
        for state in self.accept_states:
            star_tf[(state, '')] = { self.start_state }
        star_accepts = self.accept_states | { star_start }
        return NFA(star_tf, star_start, star_accepts)

    @staticmethod
    def fit(regex, alphabet=set(printable) - {'(', ')', '|', '*'}):
        """Takes a regular expression and an alphabet (i.e., a set of one-character strings) as input; returns an NFA that recognises
        the language defined by that regular expression and that alphabet.
        
        The alphabet parameter is optional; it's default value is string.printable -- i.e., the set of "printable" characters,
        which includes the standard ASCII letters and digits, and most common punctuation and white space.

        Actually, that's not quite right -- the default value is string.printable *minus* parentheses, the vertical bar, the star symbol,
        and the tilde, for reasons that I will explain presently.

        As of now, the syntax of the regular expressions that this method takes as input is very simple -- much simpler than the
        standard python regular expresssions. All characters are intepreted as literals for symbols in the alphabet except for '(', '')',
        '|', '*', '•', '€' and 'Ø'. The parentheses, vertical bar and star mean what you'd expect them to mean if you are familiar with 
        regular expressions as written in programming languages. '•' (option-8 on a mac keyboard) means concatenation. 
        You can leave concatentation implicit, as is usual; no need to write '•'' explicitly if you don't want to. But it gets used internally. 
        '€' (option-shift-2) is used to match the empty string (because it kind of looks like an epsilon); there's no other way to match, 
        for instance, {'', '0'} with the current syntax. (Quick challenge: it's not totally obvious how to match the empty string in normal python regex syntax either, 
        though it can be done; give it a go.) 'Ø' (option-shift-o) represents the empty set; you can match to the empty language with it.

        For reaons related to the above, the characters '(', ')', '|', '*', '•', '€' and 'Ø' cannot be symbols in the alphabet of the NFA.
        (My apologies to speakers of Scandinavian languages for the last one; I am very against English chauvinism, but your letter is so very
        close to the empty-set symbol. If, by some miracle, there is someone who cares about this, I will change the symbol for empty-set.)

        In the absence of parentheses, the order of operations is: `*`, then `•`, then `|`.

        I realise the simplicity of the allowed syntax is lame; some day it might be better.

        The method uses a version of Dijkstra's shunting yard algorithm to parse the regex and build the NFA.

        The method will raise a ValueError exception if any of the following conditions hold:
            1. the alphabet contains any of the verboten characters -- i.e.,`(`, `)`, `|`, `*`, `•`, `€` and `Ø`,
            2. the input regex string contains a character not in the alphabet, and not one of the above veboten characters,
            3. the input regex contain a binary operator followed by an operator, or
            4. the input regex does not have properly matching parentheses.
        """
        operators = ['sentinel', '|', '•', '*']
        parentheses = ['(', ')']
        empties = ['€', 'Ø']
        not_symbols = operators + parentheses + empties

        operator_to_operation = {
            '|': NFA.__or__,
            '•': NFA.__add__
        }        

        _error_message(
            bad_set=set(not_symbols) & set(alphabet),
            message_singular="Alphabet cannot contain character {}.",
            message_plural="Alphabet cannot contain characters {}."
        )

        def fit_empty(empty):
            tf = {pair: set() for pair in product({'q1'}, alphabet)}
            accept_states = set() if empty == 'Ø' else {'q1'}
            return NFA(tf, 'q1', accept_states)

        def fit_symbol(symbol):
            tf = { pair: set() for pair in product({'q1', 'q2'}, alphabet) }
            tf[('q1', symbol)] = {'q2'}
            return NFA(tf, 'q1', {'q2'})

        def pre_process(regex):
            first_char = regex[0]
            if first_char in operators:
                raise ValueError("Regex cannot start with '{}'.".format(first_char))
            processed = ''
            paren_count = 0
            for char in regex:
                if char in alphabet or char == '(':
                    if len(processed) > 0:
                        processed += '•' if processed[-1] not in {'(', '|'} else ''
                if char not in alphabet and char not in not_symbols:
                    raise ValueError("Regex contains character '{}' that is not in alphabet and not an accepted regex character.".format(char))
                if char in operators and processed[-1] in {'|', '•'}:
                    raise ValueError("Regex contains binary operator followed by an operator; not cool.")
                if char == '(':
                    paren_count += 1
                if char == ')':
                    paren_count -= 1
                if paren_count < 0:
                    raise ValueError("Right parenthesis occurs in regex withour matching left parenthesis.")
                processed += char
            if paren_count > 0:
                raise ValueError("Left parenthesis occurs in regex without matching right parenthesis.")
            return processed

        
        machine_stack = []
        operator_stack = ['sentinel']
        
        def binary_operate():
            right_operand = machine_stack.pop()
            left_operand = machine_stack.pop()
            machine = operator_to_operation[operator_stack.pop()](left_operand, right_operand)
            machine_stack.append(machine)

        regex = pre_process(regex)
        for char in regex:
            if char == 'Ø' or char == '€':
                machine_stack.append(fit_empty(char))
            elif char in alphabet:
                machine_stack.append(fit_symbol(char))
            elif char == '*':
                machine_stack[-1] = machine_stack[-1].star()
            elif char in operators:
                compare = lambda operator: operators.index(operator) - operators.index(operator_stack[-1])
                if operator_stack[-1] in parentheses or compare(char) > 0:
                    operator_stack.append(char)
                else:
                    while operator_stack[-1] not in parentheses and compare(char) <= 0:
                       binary_operate()
                    operator_stack.append(char)
            elif char == '(':
                operator_stack.append(char)
            else:
                while operator_stack[-1] != '(':
                    binary_operate()
                operator_stack.pop()
        while len(operator_stack) > 1:
            binary_operate()
        machine = machine_stack.pop()
        return machine


class DFA(_FSA):
    """A deterministic finite automaton class. Takes three parameters: a transition function, a start state and a set of accept states, in that order.

    The transition function should be specified as a dictionary with tuple keys. These keys implicitly define the dfa's state-set and alphabet; the first elements of the tuples represent the fsa's states, and the second elements are the symbols in the alphabet.

    The dfa expects the symbols of the alphabet to be one character strings. States can be anything hashable. (Note that, for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

    The class will raise a ValueError exception on instantiation if any of the following are true:
      * the start state is not a member of the set of states inferred from the transition function;
      * the set of accept states is not a subset of the set of states inferred from the transition function;
      * the range of the transition function is not a subset of the set of states inferred from the transition function;
      * a member of the alphabet inferred from the transition function is not a one-character string;
      * the transition function is missing a case -- i.e., it is not the case that every pair of a state and a symbol is in the domain of the transition function.
    The exception message will specify which of these above conditions things triggered the exception, and which states/symbols are the source of the problem."""
   
    def __or__(self, other):
        """Let A be the language recognised by dfa1, and B be the language recognized by dfa2. `dfa1 | dfa2` returns a dfa that recognizes A union B. The states of dfa1 | dfa2 are ordered pairs of states from dfa1 and dfa2. There is no problem with the input DFAs having different alphabets."""

        union_alphabet = self.alphabet | other.alphabet
        def maybe_add_state(dfa1, dfa2):
            new_tf = dfa1.transition_function.copy()
            new_states = dfa1.states.copy()
            extra_symbols = dfa2.alphabet - dfa1.alphabet
            if extra_symbols != set():
                error_state = self._get_new_state(dfa1.states)
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

    def __add__(self, other):
        """Let A be the language recognised by dfa1, B be the language recognised by dfa2. `dfa1 + dfa2` returns a DFA that recognises the set of all concatenations of strings in A with strings in B. This DFA operator is parasitic on the NFA operator; it converts the input DFAs into NFAs, uses the NFA '+', then converts the result back to a DFA. That makes for a relatively simple but, sadly, computationally expensive algorith. For that reason, I recommend you don't `+` dfas with large numbers of states."""
        return (self.non_determinize() + other.non_determinize()).determinize()

    def _gnfize(self):
        gnfa_tf = {}
        for state1, symbol in self.transition_function.keys():
            state2 = self.transition_function[(state1, symbol)]
            if (state1, state2) in gnfa_tf.keys():
                gnfa_tf[(state1, state2)] += '|' + symbol
            else:
                gnfa_tf[(state1, state2)] = symbol
        gnfa_start = self._get_new_state(self.states)
        gnfa_accept = self._get_new_state(self.states | {gnfa_start})
        gnfa_tf[(gnfa_start, self.start_state)] = '€'
        for state in self.accept_states:
            gnfa_tf[(state, gnfa_accept)] = '€'
        for state1, state2 in product(self.states | {gnfa_start}, self.states | {gnfa_accept}):
            if not (state1, state2) in gnfa_tf.keys():
                gnfa_tf[(state1, state2)] = 'Ø'
        return _GNFA(gnfa_tf, set(self.states), gnfa_start, gnfa_accept)

    def _good_range(self):
        transition_range = set(self.transition_function.values())
        bad_range = transition_range - self.states
        _error_message(
            bad_set=bad_range,
            message_singular=("State {} in the range of the transition "
                              "function is not in the fsa's state set."),
            message_plural=("States {} in the range of the transition "
                            "function are not in the fsa's state set.")
        )

    def accepts(self, string):
        """`my_dfa.accepts("some string")` returns `True` if my_dfa accepts "some string", and `False` otherwise. Will raise a ValueError exception is the string contains symbols that aren't in the DFA's alphabet."""
        _check_input(string=string, alphabet=self.alphabet)
        current_state = self.start_state
        for symbol in string:
            current_state = self.transition_function[(current_state, symbol)]
        return False if current_state not in self.accept_states else True

    def encode(self):
        """Let A be the language accepted by dfa. `dfa.encode()` returns a regex string that generates A. That regex string is liable to be much more complicated than necessary; maybe I'll figure out how to improve on average simplicity, eventually. Note that the regex language I use is much simpler than the standard python regex language (though it is technically equivalent in expressive power)."""
        gnfa = self._gnfize()
        while len(gnfa.states) > 2:
            gnfa = gnfa.reduce()
        return gnfa.transition_function[(gnfa.start_state, gnfa.accept_state)]

    def non_determinize(self):
        """Convenience method that takes a DFA instance and returns an NFA instance."""
        nd_transition_function = {key: {value} for key, value in self.transition_function.items()}
        return NFA(nd_transition_function, self.start_state, self.accept_states)

