import re

class CFG:
    def __init__(self, rules, start_variable):
        self.rules = rules
        self._check_rules()
        self.variables = set(self.rules.keys())
        self.terminals = set.union(*map(self._parse_values, self.rules.values()))
        self._check_terminals()
        self.start_variable = start_variable
        self._check_start()

    def _check_rules(self):
        if type(self.rules) != dict:
            raise ValueError("Rules parameter should be a dictionary.")
        bad_variables = {x for x in self.rules if type(x) != str}
        self._error_message(
            bad_variables,
            "Variable {} is not a string.",
            "Variables {} are not strings."
        )
        bad_values = {x for x in self.rules.values() if type(x) != set and type(x) != frozenset}
        self._error_message(
            bad_values,
            "Value {} of rules dictionary is not either a set or frozenset.",
            "Values {} of rules dictionary are not either sets or frozensets."
        )
        members = set.union(*list(self.rules.values()))
        bad_members = {x for x in members if type(x) != str}
        self._error_message(
            bad_members,
            "Value member {} is not a string.",
            "Value members {} are not strings."
        )

    def _check_terminals(self):
        if self.terminals == set():
            raise ValueError("There are no terminals in the rule dictionary values.")

    def _check_start(self):
        if self.start_variable not in self.variables:
            raise ValueError("Start variable not in the CFG's variable set.")

    def _parse_values(self, substitution_set):
        parse = lambda substitution: set(re.split('|'.join(self.variables), substitution)) - {''}
        return set.union(*map(parse, substitution_set))

    def _error_message(self, bad_set, message_singular, message_plural):
        if bad_set != set():
            quoted_members = {"'{}'".format(x) for x in bad_set}
            if len(quoted_members) == 1:
                raise ValueError(message_singular.format(*quoted_members));
            else:
                raise ValueError(message_plural.format((", ").join(quoted_members)))

    def get_rules(self):
        return self.rules.copy()

    def get_start_variable(self):
        return self.start_variable

    def get_variables(self):
        return self.variables.copy()

    def get_terminals(self):
        return self.terminals.copy()

    def chomsky_normalize(self):

        def get_new_variable(variable_set):
            new_variable = 'V';
            while new_variable in variable_set:
                new_variable = new_variable + '`'
            return new_variable
        rule_set = {(v, s) for v in self.rules for s in self.rules[v]}
        normalized_start = get_new_variable(self.variables)
        rule_set.add((normalized_start, self.start_variable))
        removed_rules = set()
        rule_variables = {v for v, s in rule_set}
        rule_substitutions = {s for v, s in rule_set}
        while rule_substitutions & (rule_variables | {'€'}) != set():
            for rule in list(rule_set):
                variable, substitution = rule
                if substitution in rule_variables | {'€'}:
                    rule_set.remove(rule)
                    removed_rules.add(rule)
                    for other_rule in list(rule_set):
                        other_variable, other_substitution = other_rule
                        if substitution == '€':
                            if variable in other_substitution:
                                for match in re.finditer(variable, other_substitution):
                                    new_substitution = other_substitution[:match.start()] + other_substitution[match.end()+1:]
                                    if new_substitution == '':
                                        new_substitution = '€'
                                    new_rule = (other_variable, new_substitution)
                                    if not (new_rule in removed_rules):
                                        rule_set.add(new_rule)
                        else:
                            if other_variable == substitution:
                                new_rule = (variable, other_substitution)
                                if not (new_rule in removed_rules):
                                    rule_set.add(new_rule)
            rule_substitutions = {s for v, s in rule_set}
            rule_variables = {v for v, s in rule_set}

        def parse_substitution(string):
            words = {v for v, s in rule_set} | self.terminals
            word_candidate = ''
            parsed = []
            for char in string:
                word_candidate += char
                if char in words:
                    parsed.append(word_candidate)
                    word_candidate = ''
            return parsed

        three_word_rules = {rule for rule in rule_set if len(parse_substitution(rule[1])) >=3}
        while three_word_rules != set():
            for rule in three_word_rules:
                variable, substitution = rule
                rule_set.remove(rule)
                parsed_substitution = parse_substitution(substitution)
                last_variable = variable
                for word in parsed_substitution[:-2]:
                    new_variable = get_new_variable({v for v, s in rule_set | {(variable, substitution)}})
                    new_rule = (last_variable, word + new_variable)
                    rule_set.add(new_rule)
                    last_variable = new_variable
                final_rule = (last_variable, ''.join(parsed_substitution[-2:]))
                rule_set.add(final_rule)
            three_word_rules = {rule for rule in rule_set if len(parse_substitution(rule[1])) >= 3}
        
        def get_bad_remaining_rules():
            bad_rules = set()
            for rule in rule_set:
                parsed_substitution = parse_substitution(rule[1])
                if len(parsed_substitution) == 2 and (self.terminals & set(parsed_substitution) != set()):
                    bad_rules.add(rule)
            return bad_rules

        bad_remaining_rules = get_bad_remaining_rules()
        while bad_remaining_rules != set():
            print(rule_set)
            print(bad_remaining_rules)
            print("+++++++++++++++++++")
            for rule in bad_remaining_rules:
                variable, substitution = rule
                parsed_substitution = parse_substitution(substitution)
                for word in set(parsed_substitution):
                    if word in self.terminals:
                        new_variable = get_new_variable({v for v, s in rule_set})
                        rule_set.add((new_variable, word))
                        for other_rule in get_bad_remaining_rules():
                            other_variable, other_substitution = other_rule
                            if word in other_substitution:
                                rule_set.remove(other_rule)
                                new_substitution = other_substitution.replace(word, new_variable)
                                rule_set.add((other_variable, new_substitution))
            bad_remaining_rules = get_bad_remaining_rules()

        normalized_rules = {}
        for rule in rule_set:
            variable, substitution = rule
            if variable in normalized_rules:
                normalized_rules[variable].add(substitution)
            else:
                normalized_rules[variable] = {substitution}
        return CFG(normalized_rules, normalized_start)
