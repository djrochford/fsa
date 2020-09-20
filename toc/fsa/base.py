"""
Base class and utility functions used in both fsa and fst files.
"""

from itertools import product
from typing import (
    AbstractSet, Dict, FrozenSet, Iterable, Mapping, Tuple, Union
)

State = str

Symbol = str

TransitionFunction = Mapping[
    Tuple[State, Symbol],
    Union[State, AbstractSet[State], Tuple[State, Symbol]]
]


class _Base:

    def __init__(
            self,
            *,
            transition_function: TransitionFunction,
            start_state: str
    ):
        self._transition_function = transition_function
        self._start_state = start_state
        self._states = _extract_states_alphabet(
            self._transition_function.keys()
        )[0]

    @property
    def transition_function(self) -> Dict:
        """
        Getter for the finite state machine's transition function. Returns a
        a copy of the transition-function; the transition function will not
        be mutated by mutating the copy.
        """
        return dict(self._transition_function)

    @property
    def start_state(self) -> State:
        """
        Getter for the finite state machine's start state.
        """
        return self._start_state

    @property
    def states(self) -> FrozenSet[str]:
        """
        Gett for finite state machines's set of states.
        """
        return self._states

    def _well_defined(self) -> None:
        self._good_start()
        self._good_range()

    def _good_start(self) -> None:
        if self._start_state not in self._states:
            raise ValueError(f"Start state '{self._start_state}' is not a "
                             "member of the fsm's state set.")

    def _good_range(self) -> None:
        raise NotImplementedError

    def _good_domain(self, alphabet: Iterable) -> None:
        bad_pairs = (set(product(self.states, alphabet))
                     - self.transition_function.keys())
        _error_message(
            bad_set=bad_pairs,
            message_singular=("Pair {} is missing from transition function "
                              "domain."),
            message_plural=("Pairs {} are missing from transition function "
                            "domain.")
        )


def _extract_states_alphabet(
        pairs: Iterable[Tuple[State, Symbol]]
) -> Tuple[FrozenSet[State], FrozenSet[Symbol]]:
    [states_tuple, alphabet_tuple] = zip(*pairs)
    return (frozenset(states_tuple), frozenset(alphabet_tuple) - {""})


def _error_message(
        *, bad_set: AbstractSet, message_singular: str, message_plural: str
) -> None:
    if bad_set:
        quoted_members = {"'{}'".format(x) for x in bad_set}
        if len(quoted_members) == 1:
            raise ValueError(message_singular.format(*quoted_members))
        raise ValueError(message_plural.format((", ").join(quoted_members)))


def _good_alphabet(*, alphabet: Iterable, name: str) -> None:
    _error_message(
        bad_set={
            x for x in alphabet if not (isinstance(x, str) and len(x) == 1)
        },
        message_singular=("Symbol {} in the " + name + " is not single "
                          "character string."),
        message_plural=("Symbols {} in the " + name + " are not single "
                        "character strings.")
    )


def _check_input(*, string: str, alphabet: AbstractSet) -> None:
    _error_message(
        bad_set=set(string) - alphabet,
        message_singular="Symbol {} not in fsa's alphabet",
        message_plural="Symbols {} not in fsa's alphabet"
    )
