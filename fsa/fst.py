from base import _Base

class FST(_Base):
    def __init__(self, transition_function, start_state):
        self.transition_function = transition_function
        self.start_state = start_state
        self.states, self.input_alphabet = self._extract_states_alphabet(self.transition_function.keys())
        self.range, self.output_alphabet = self._extract_states_alphabet(self.transition_function.values())
        self._well_defined()

    def _well_defined(self):
        self._good_start()
        self._good_alphabet(self.input_alphabet, "input alphabet")
        self._good_alphabet(self.output_alphabet, "output alphabet")
        self._good_range()
        self._good_domain(self.input_alphabet)

    def _good_range(self):
        bad_range = self.range - self.states
        self._error_message(
            bad_range,
            "State {} in the range of the transition function is not in the fsa's state set.",
            "States {} in the range of the transition function are not in the fsa's state set."
        )