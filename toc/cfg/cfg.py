"""
Context-Free Grammar Class
"""
from itertools import chain, combinations
from typing import (
    AbstractSet, Dict, FrozenSet, Mapping, Sequence, Set, Tuple, Union
)


class CFG:
    """
    A context-free grammar class. Takes two parameters: the grammar's rules,
    and the start variable, in that order.

    The rules should be specified as a dictionary with string keys and set (or
    frozenset) values. Each member of the set is a possible substitution for
    that variable; a substitution should be a tuple of strings, or, if you
    wish, in the case of single-variable substitutions, a string.

    The variables and terminals of the grammar are inferred from the rule
    dictionary. All keys are assumed to be variables of the grammar; everything
    that appears in a substitution that isn't a variable is assumed to be a
    terminal.

    You can specify empty substitutions using '€' (opt-shift-2, on a mac). That
    symbol the closest thing to an epsilon you can access easily from the
    keyboard.

    The class will raise a ValueError exception on instantiation if any of the
    following are true:
        1. the first (rule) parameter is not a dictionary;
        2. the rule dictionary contains a non-string key;
        3. the rule dictionary contains a value that is neither a set nor a
        frozenset;
        4. one of the set-values of the rule dictionary has a non-string
        member;
        5. there are no terminals among the possible substitutions;
        6. the start-variable parameter is not one of the variables inferred
        from the rule dictionary.
    The exception message will specify which of the above conditions triggered
    the exception, and which variables/terminals were the source of the
    problem.
    """
    def __init__(
            self,
            rules: Mapping[str, AbstractSet[Union[Tuple[str, ...], str]]],
            start_variable: str
    ):
        self._rules = rules
        self._variables = frozenset(self.rules.keys())
        self._terminals = self._find_terminals()
        self._check_terminals()
        self._start_variable = start_variable
        self._check_start()

    def _find_terminals(self) -> FrozenSet[str]:
        empty: Set[Union[Tuple[str, ...], str]] = set()
        substitutions = empty.union(*self.rules.values())
        substitution_values = set()
        for substitution in substitutions:
            if isinstance(substitution, tuple):
                for value in substitution:
                    substitution_values.add(value)
            else:
                substitution_values.add(substitution)
        terminals = substitution_values - self._variables
        return frozenset(terminals)

    def _check_terminals(self) -> None:
        if self._terminals == set():
            raise ValueError(
                "There are no terminals in the rule dictionary values."
            )

    def _check_start(self) -> None:
        if self._start_variable not in self._variables:
            raise ValueError("Start variable not in the CFG's variable set.")

    @property
    def rules(self) -> Dict[str, AbstractSet[Union[Tuple[str, ...], str]]]:
        """
        Getter for `_rules` property. Returns a new `dict` version of the
        rules; mutating the returned value will not mutate the CFG's rules.
        """
        return dict(self._rules)

    @property
    def start_variable(self) -> str:
        """
        Getter for the `_start_variable` property
        """
        return self._start_variable

    @property
    def variables(self) -> FrozenSet[str]:
        """
        Getter for the `_variables` property.
        """
        return self._variables

    @property
    def terminals(self) -> FrozenSet[str]:
        """
        Getter for the `_terminals`property.
        """
        return self._terminals

    def is_valid_derivation(self, derivation: Sequence[Sequence[str]]) -> bool:
        """
        Your derivation should be in the form of a list of lists, the
        members of each list being variables or terminals of the cfg instance.
        `is_valid_derivation` returns True iff each list can be derived from
        the previous list via a rule in the CFG's rule dictionary -- i.e., it
        returns True iff the derivation encoded in your list of lists is a
        valid derivation for the relevant CFG. It returns False otherwise.
        """

        def yields(line1: Sequence[str], line2: Sequence[str]) -> bool:
            if line1 == line2:
                return True
            if len(line1) < 1:
                return False
            first_term = line1[0]
            possible_substitutes = {first_term}
            if first_term in self.variables:
                possible_substitutes = (
                    possible_substitutes | self.rules[first_term]
                )
            for substitution in possible_substitutes:
                if isinstance(substitution, str):
                    substitution = [substitution]
                is_valid = False
                if line2[:len(substitution)] == list(substitution):
                    is_valid = yields(line1[1:], line2[len(substitution):])
                if is_valid:
                    return True
            return False

        for i in range(len(derivation) - 1):
            if not yields(derivation[i], derivation[i+1]):
                return False
        return True

    def chomsky_normalize(self) -> "CFG":
        """
        Let cfg be a context-free grammar that generates language L.
        `cfg.chomky_normalize()` returns a new CFG instance that also generates
        L, but is in Chomsky Normal Form -- i.e., all possible substitutions of
        variables are either single terminals or a pair of variables (no empty
        substitutions).

        The resulting grammar is liable to much more complicated than the
        minimally-complicated, Chomsky-normalized grammar that generates L.
        Maybe some day I'll add some stuff to simplify the result.
        """
        # some pre-processing of the rules to make life easier
        rule_set = {(v, s) for v in self.rules for s in self.rules[v]}
        rule_list = list(rule_set)
        for i, rule in enumerate(rule_list):
            if isinstance(rule[1], str):
                rule_list[i] = (rule[0], (rule[1]))
        rule_set = set(rule_list)

        def deal_with_start():
            normalized_start = _get_new_variable(self.variables)
            rule_set.add((normalized_start, (self.start_variable)))
            return normalized_start

        normalized_start = deal_with_start()

        def deal_with_epilsons():
            removed_epsilons = set()
            epsilon_rules = {rule for rule in rule_set if rule[0] != normalized_start and rule[1] == ('€')}
            while epsilon_rules:
                for rule in epsilon_rules:
                    variable = rule[0]
                    rule_set.remove(rule)
                    removed_epsilons.add(rule)
                    for v, s in list(rule_set):
                        if s == (variable):
                            new_rule = (v, ('€'))
                            if new_rule not in removed_epsilons:
                                rule_set.add(new_rule)
                        else:
                            if variable in s:
                                occurences = [i for i, value in enumerate(s) if value == variable]
                                power_set_occurences = _powerset(occurences)
                                for occurence_list in power_set_occurences:
                                    new_substitution = list(s)
                                    for index in sorted(occurence_list, reverse=True):
                                        del new_substitution[index]
                                    new_rule = (v, tuple(new_substitution))
                                    rule_set.add(new_rule)
                epsilon_rules = {rule for rule in rule_set if rule[0] != normalized_start and rule[1] == ('€')}
        
        deal_with_epilsons()

        def deal_with_unit_rules():
            removed_unit_rules = set()
            unit_rules = {rule for rule in rule_set if len(rule[1]) == 1 and rule[1][0] not in self.terminals}
            while unit_rules != set():
                for rule in unit_rules:
                    variable = rule[0]
                    substitution_variable = rule[1][0]
                    rule_set.remove(rule)
                    removed_unit_rules.add(rule)
                    for v, s in list(rule_set): 
                        if v == substitution_variable and s[0] in self.terminals:
                            new_rule = (variable, s)
                            if new_rule not in removed_unit_rules:
                                rule_set.add(new_rule)
                unit_rules = {rule for rule in rule_set if len(rule[1]) == 1 and rule[1][0] not in self.terminals}

        deal_with_unit_rules()

        def deal_with_long_rules():
            variables = {v for v, s in rule_set}
            long_rules = {rule for rule in rule_set if len(rule[1]) >= 3}
            for rule in long_rules:
                rule_set.remove(rule)
                left_hand_variable = rule[0]
                for value in rule[1][:-1]:
                    new_variable = _get_new_variable(variables)
                    variables.add(new_variable)
                    new_rule = (left_hand_variable, (value, new_variable))
                    rule_set.add(new_rule)
                    left_hand_variable = new_variable
                new_rule = (left_hand_variable, (rule[1][-2], rule[1][-1]))
                rule_set.add(new_rule)

        deal_with_long_rules()

        def deal_with_bad_terminals():
            variables = {v for v, s in rule_set}
            bad_terminal_rules = {rule for rule in rule_set if len(rule[1]) == 2 and set(rule[1]) & self.terminals != set()}
            for rule in bad_terminal_rules:
                rule_set.remove(rule)
                terminal_indices = [i for i, value in enumerate(rule[1]) if value in self.terminals]
                new_rule = list(rule)
                new_variables = set()
                for i in terminal_indices:
                    new_variable = _get_new_variable(variables)
                    variables.add(new_variable)
                    new_variables.add(new_variable)
                    new_rule[1] = list(new_rule[1])
                    new_rule[1][i] = new_variable
                    other_new_rule = (new_variable, rule[1][i])
                    rule_set.add(other_new_rule)
                rule_set.add((new_rule[0], tuple(new_rule[1])))

        deal_with_bad_terminals()

        #convert rule_set to standard rule dictionary
        normalized_rules: Dict[str, Set[Union[Tuple[str, ...], str]]] = {}
        for rule in rule_set:
            variable, substitution = rule
            if variable in normalized_rules:
                normalized_rules[variable].add(substitution)
            else:
                normalized_rules[variable] = {substitution}

        return CFG(normalized_rules, normalized_start)


def _error_message(bad_set: AbstractSet, message_singular: str, message_plural: str):
    if bad_set != set():
        quoted_members = {"'{}'".format(x) for x in bad_set}
        if len(quoted_members) == 1:
            raise ValueError(message_singular.format(*quoted_members));
        else:
            raise ValueError(message_plural.format((", ").join(quoted_members)))

# first some utility procedures
def _get_new_variable(variable_set):
    new_variable = 'V'
    counter = 1
    while new_variable in variable_set:
        new_variable = 'V' + str(counter)
        counter += 1
    return new_variable

# powerset code an itertools recipe,
# from https://docs.python.org/3/library/itertools.html#recipes
def _powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(
        combinations(s, r) for r in range(len(s)+1)
    )
