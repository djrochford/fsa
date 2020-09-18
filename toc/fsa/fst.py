"""
File for the finite-state transducer class.
"""
from typing import Hashable, Mapping, Set, Tuple, TypeVar

from .base import (
    _Base,
    _extract_states_alphabet,
    _error_message,
    _good_alphabet,
    _check_input,
)

T = TypeVar("T", bound=Hashable)

TransitionFunction = Mapping[Tuple[T, str], Tuple[T, str]]


class FST(_Base):
    """
    A finite state transducer class. Takes two parameters: a transition
    function, and a start state, in that order.

    The transition function should be specified as a dictionary with tuple
    keys and values. These keys implicitly define the fst's state-set and input
    alphabet; the first elements of the tuples represent the fst's states, and
    the second elements are the symbols in the alphabet.

    Similarly, the values should be tuples with the first element a state, the
    second member a symbol in the output alphabet, and the output alphabet
    (though not the state set) is implicitly defined by these values.

    The fst expects the symbols of both alphabets to be one character strings.
    States can be anything hashable. (Note that, for reasons of hashability,
    you'll need to use frozensets, rather than sets, if you want to have sets
    as states.)

    The class will raise a ValueError exception on instantiation if any of the
    following are true:
        1. the start state is not a member of the set of states inferred from
        the transition function;
        2. a member of the input alphabet inferred from the transition function
        is not a one-character string;
        3. a member of the output alphabet inferred from the transition
        function is not a one-character string;
        4. the range of the transition function is not a subset of the
        state-set inferred from the transition function;
        5. the transition function is missing cases -- i.e., it is not the case
        that every pair of a state and a symbol in the input alphabet is in the
        domain of the transition function.
    The exception message will specify which of these five conditions things
    triggered the exception, and which states/symbols are the source of the
    problem.
    """
    def __init__(
            self, transition_function: TransitionFunction, start_state: T
    ):
        super().__init__(
            transition_function=transition_function, start_state=start_state
        )
        self._states, self._input_alphabet = _extract_states_alphabet(
            self.transition_function.keys()
        )
        self.range, self._output_alphabet = _extract_states_alphabet(
            self.transition_function.values()
        )
        self._well_defined()

    def _well_defined(self) -> None:
        super()._well_defined()
        _good_alphabet(alphabet=self.input_alphabet, name="input alphabet")
        _good_alphabet(alphabet=self.output_alphabet, name="output alphabet")
        self._good_domain(self.input_alphabet)

    def _good_range(self) -> None:
        bad_range = self.range - self.states
        _error_message(
            bad_set=bad_range,
            message_singular=("State {} in the range of the transition "
                              "function is not in the fsa's state set."),
            message_plural=("States {} in the range of the transition "
                            "function are not in the fsa's state set.")
        )

    @property
    def input_alphabet(self) -> Set[str]:
        """
        Getter for `input_alphabet` property. Returns a copy of the input
        alphabet; mutating the copy will not mutate the fst's input alphabet.
        """
        return self._input_alphabet.copy()

    @property
    def output_alphabet(self) -> Set[str]:
        """
        Getter for `output_alphabet` property. Returns a copy of the output
        alphabet; mutating the copy will not mutate the fst's output alphabet.
        """
        return self._output_alphabet.copy()

    def process(self, string: str) -> str:
        """
        Takes a string as input, and returns a string as output.
        Specifically, it returns the string specified by the transition
        function.
        """
        _check_input(string=string, alphabet=self.input_alphabet)
        current_state = self.start_state
        output = ""
        for input_symbol in string:
            (next_state, output_symbol) = self.transition_function[
                (current_state, input_symbol)
            ]
            output += output_symbol
            current_state = next_state
        return output
