import re

class CFG:
    def __init__(self, rules, start_variable):
        self.rules = rules
        self._check_rules()
        self.variables = set(self.rules.keys())
        self.terminals = set.union(*map(self._parse_value, self.rules.values()))
        self._check_terminals()
        self.start_variable = start_variable
        self._check_start()

    def _check_rules(self):
        if type(self.rules) != dict:
            raise ValueError("Rules parameter should be a dictionary.")
        bad_variables = {x for x in self.rules.keys() if type(x) != str}
        self._error_message(
            bad_variables,
            "Variable {} is not a string.",
            "Variables {} are not strings."
        )
        bad_values = {x for x in self.rules.values() if type(x) != str}
        self._error_message(
            bad_values,
            "Value {} of rule dictionary is not a string.",
            "Values {} of rules dictionary are not strings."
        )

    def _check_terminals(self):
        if self.terminals == set():
            raise ValueError("There are no terminals in the rule dictionary values.")

    def _check_start(self):
        if self.start_variable not in self.variables:
            raise ValueError("Start variable not in the CFG's variable set.")

    def _parse_value(self, value):
        values = value.split('|')
        parse = lambda value: set(re.split('|'.join(self.variables), value)) - {'', '|'}
        return set.union(*map(parse, values))

    def _error_message(self, bad_set, message_singular, message_plural):
        if bad_set != set():
            quoted_members = {"'{}'".format(x) for x in bad_set}
            if len(quoted_members) == 1:
                raise ValueError(message_singular.format(*quoted_members));
            else:
                raise ValueError(message_plural.format((", ").join(quoted_members)))

    # def _well_defined(self):
    #     self._good_variables(),
    #     self._good_terminals(),
    #     self._good_start()

    # def _good_variables(self):
    #     bad_variables = { x for x in self.variables if not type(x) == str }
    #     self._error_message(
    #       bad_variables,
    #       "Variable {} is not a string.",
    #       "Variables {} are not strings."
    #     )

    # def _good_terminals(self):
    #     if terminals == set():
    #         raise ValueError("Rules contain no terminals.")
    #     bad_terminals = { x for x in terminals if not type(x) == str }
    #     self._error_message(
    #         bad_terminals
    #         "Terminal {} is not a string."
    #         "Terminals {} are not strings."
    #     )

    # def _good_start(self):
    #     if self.star_variable not in self.variables:
  
    #         raise ValueError("Start variable not in CFG's variable set.")
