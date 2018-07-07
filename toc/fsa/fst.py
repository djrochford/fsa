from .base import _Base

class FST(_Base):
    """A finite state transducer class. Takes two parameters: a transition function, and a start state, in that order.

    The transition function should be specified as a dictionary with tuple keys and values. 
    These keys implicitly define the fst's state-set and input alphabet; the first elements of the tuples represent the
    fst's states, and the second elements are the symbols in the alphabet.

    Similarly, the values should be tuples with the first element a state, the second member a symbol in the output alphabet, and
    the output alphabet (though not the state set) is implicitly defined by these values.

    The fst expects the symbols of both alphabets to be one character strings. States can be anything hashable. (Note that,
    for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

    The class will raise a ValueError exception on instantiation if any of the following are true:
        1. the start state is not a member of the set of states inferred from the transition function;
        2. a member of the input alphabet inferred from the transition function is not a one-character string;
        3. a member of the output alphabet inferred from the transition function is not a one-character string;
        4. the range of the transition function is not a subset of the state-set inferred from the transition function;
        5. the transition function is missing cases -- i.e., it is not the case that every pair of a state and a symbol 
        in the input alphabet is in the domain of the transition function.
    The exception message will specify which of these five conditions things triggered the exception, and which states/symbols
    are the source of the problem."""
    def __init__(self, transition_function, start_state):
        super().__init__(transition_function, start_state)
        self.states, self.input_alphabet = self._extract_states_alphabet(self.transition_function.keys())
        self.range, self.output_alphabet = self._extract_states_alphabet(self.transition_function.values())
        self._well_defined()

    def _well_defined(self):
        super()._well_defined()
        self._good_alphabet(self.input_alphabet, "input alphabet")
        self._good_alphabet(self.output_alphabet, "output alphabet")
        self._good_domain(self.input_alphabet)

    def _good_range(self):
        bad_range = self.range - self.states
        self._error_message(
            bad_range,
            "State {} in the range of the transition function is not in the fsa's state set.",
            "States {} in the range of the transition function are not in the fsa's state set."
        )
    def get_input_alphabet(self):
        return self.input_alphabet.copy()

    def get_output_alphabet(self):
        return self.output_alphabet.copy()

    def process(self, string):
        """Takes a string as input, and returns a string as output.
        Specifically, it returns the string specified by the transition function."""
        self._check_input(string, self.input_alphabet)
        current_state = self.start_state
        output = ''
        for input_symbol in string:
            (next_state, output_symbol) = self.transition_function[(current_state, input_symbol)]
            output += output_symbol
            current_state = next_state
        return output 
