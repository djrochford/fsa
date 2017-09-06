from base import _Base

class FST(_Base):
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
        self._check_input(string, self.input_alphabet)
        current_state = self.start_state
        output = ''
        for input_symbol in string:
            (next_state, output_symbol) = self.transition_function[(current_state, input_symbol)]
            output += output_symbol
            current_state = next_state
        return output 
