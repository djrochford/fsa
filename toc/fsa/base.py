"""
Base class used internally.
"""

from itertools import product
from typing import Hashable, Iterable, Mapping, Set, Tuple, Union

TransitionFunction = Mapping[
    Tuple[Hashable, str], Union[Tuple[Hashable, str], Set[Hashable], Hashable]
]


def _extract_states_alphabet(
        pairs: Iterable[Tuple[Hashable, str]]
) -> Tuple[Set[Hashable], Set[str]]:
    [states_tuple, alphabet_tuple] = zip(*pairs)
    states = set(states_tuple)
    alphabet = set(alphabet_tuple) - {""}
    return (states, alphabet)


def _error_message(
        bad_set: set, message_singular: str, message_plural: str
) -> None:
    if bad_set != set():
        quoted_members = {"'{}'".format(x) for x in bad_set}
        if len(quoted_members) == 1:
            raise ValueError(message_singular.format(*quoted_members))
        raise ValueError(message_plural.format((", ").join(quoted_members)))


class _Base:

    def __init__(
            self,
            transition_function: TransitionFunction,
            start_state: Hashable
    ):
        self._transition_function = transition_function
        self._start_state = start_state
        self._states = _extract_states_alphabet(self._transition_function.keys())[0]

    @property
    def transition_function(self):
        return dict(self._transition_function)

    @property
    def start_state(self):
        return self._start_state

    @property
    def states(self):
        return self._states

    def _well_defined(self) -> None:
        self._good_start()
        self._good_range()

    def _good_start(self) -> None:
        if self.start_state not in self.states:
            raise ValueError("Start state '{}' is not a member of the fsa's state set.".format(self.start_state))

    def _good_alphabet(self, alphabet: Iterable, name: str) -> None:
        bad_symbols = {x for x in alphabet if not (type(x) is str and len(x) == 1)}
        _error_message(
            bad_symbols,
            "Symbol {} in the " + name + " is not single character string.",
            "Symbols {} in the " + name + " are not single character strings."
        )

    def _good_range(self):
        raise NotImplementedError

    def _good_domain(self, alphabet: Iterable) -> None:
        bad_pairs = set(product(self.states, alphabet)) - self.transition_function.keys()
        _error_message(
            bad_pairs,
            "Pair {} is missing from transition function domain.",
            "Pairs {} are missing from transition function domain."
        )

    def _check_input(self, string: str, alphabet: set):
        bad_symbols = set(list(string)) - alphabet
        _error_message(
            bad_symbols,
            "Symbol {} not in fsa's alphabet",
            "Symbols {} not in fsa's alphabet"
        )

    def get_states(self):
        return self.states.copy()

    def get_transition_function(self):
        return self.transition_function.copy()

    def get_start_state(self):
        return self.start_state
